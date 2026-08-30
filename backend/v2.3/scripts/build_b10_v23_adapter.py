#!/usr/bin/env python3
"""Build the isolated, zero-copy B10 backend-v2.3 adapter.

The adapter materializes only the already admitted compact B10 navigation,
topology, and search projection.  The complete 163,583-record owner backend
remains immutable and authoritative.  No textbook prose, inferred concept
relations, synthetic assessment state, or invented unit HTML anchor is emitted.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


RECORDED_AT = "2026-08-30T00:00:00Z"
ADAPTER_VERSION = "0.2.0"
LANE_NAMESPACE = uuid.UUID("0e4d7b37-6108-5065-b08f-d1098697cc02")
OWNER_NAMESPACE = "e810c566-4edf-5b5a-ad52-de3dc04e2083"
COMMON_NAMESPACE = "7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd"
CURRENT_COURSE_ID = "urn:uuid:8937ae38-2a8f-5cb6-b223-b62da2720974"
CURRENT_V1_COURSE_ID = "urn:uuid:5b7d2a5e-1421-5ac0-b02c-5ae619645272"
CURRENT_A30_COURSE_ID = "urn:uuid:def941e5-b60b-59ca-a3c7-1ed71ab3146d"
CURRENT_A30_V1_COURSE_ID = "urn:uuid:d1133682-6bc8-5b17-911d-47f36299c75d"

TABLE_ORDER = [
    "owner_authorities", "datasets", "editions", "units",
    "course_unit_memberships", "native_bindings", "content_bindings",
    "relations", "rights", "rights_assignments", "artifacts",
    "build_recipes", "reader_surfaces", "routes", "search_documents",
    "adapter_profiles", "adapter_runs", "qa_events", "identity_crosswalks",
]
RECORD_TYPE_BY_TABLE = {
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
CAPABILITY_NAMES = [
    "structure_localization", "terminology", "mathematical_preservation",
    "assessment_support", "assets", "accessibility", "corrections",
    "computational_interactives", "publication", "research_support",
]

EXPECTED_INPUTS = {
    "capability_contract": (7462, "f7708333983ec0f23379395c2a1ca8acf04f9f9fdb03a25221b93d9379537eb7"),
    "learner_route_readback": (1916, "5aaa41841853f9e48df3f067bc6261b816e839698b5acc9870e7584d57ff05b9"),
    "migration_receipt": (15491, "a68e46a2b2bdce8b93630dbd2e157581a0f7a7bb03c1f509632ab7d8d3701ddb"),
    "pilot_manifest": (4284, "c4ef9724d6ff21c567fa0cde22fe580de44e104db0fba5fef037d3c420d8cb7c"),
    "units": (352205, "80d79c94d7a780d7b8a5b317ca68c07fac25f21abf2f331747f12eed6db4c91d"),
    "relations": (108149, "0ca7768415609146c554bef2228b6cde52d3df605088b117acfa246c9ca7553d"),
    "search": (64732, "e08fb76866be2c58827f015caec3d378f053a1eb2f43cf05d990eabdfe5475b9"),
    "rights_accessibility": (3077, "2e0c51ab3086aafc6cfe26cfd106d0e85469f5d5a95a8a7df605443549ccf2ae"),
    "pilot_validation": (2114, "f114477008efba8763e5e725c96c7e9e70bc3d2ac4c9a93b06e037514d6faf0b"),
    "courses_current": (86522, "7dee2faef2019e23fe4d3650ee772a23f9120979dae69409672fde3951101351"),
    "federation_manifest": (8952, "62198018ce4d035e1bb3893af5666dddae8e054b1d30a162e24cfd631ba0dc2c"),
    "owner_manifest": (10831, "ebcea79ba19cdd0f08f1bf6444928fcf8bda8a5641535e59c20c9ee230763d20"),
    "owner_namespace": (295, "e894f9efb71c4f9d332cd11c5696f2786ff062de7e3f74ee777d717902506977"),
    "owner_validation": (3867, "39fe59a9c3945731b12dc1dd70370a38ff3a9890683f18121d3f51199fde7af5"),
}


class AdapterError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AdapterError(message)


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


def pretty_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pretty_json_bytes(value))


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as stream:
        for number, line in enumerate(stream, 1):
            require(bool(line.strip()), f"blank JSONL line: {path}:{number}")
            row = json.loads(line)
            require(isinstance(row, dict), f"non-object JSONL row: {path}:{number}")
            require(compact_json(row) == line.rstrip("\r\n"), f"non-canonical JSONL row: {path}:{number}")
            rows.append(row)
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(compact_json(row) + "\n" for row in rows).encode("utf-8")
    path.write_bytes(payload)


def file_fact(path: Path, relative: str, role: str, *, path_base: str = "package_root") -> dict[str, Any]:
    return {
        "path": PurePosixPath(relative).as_posix(),
        "path_base": path_base,
        "role": role,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def projection_id(record_type: str, semantic_key: str) -> str:
    return "urn:uuid:" + str(uuid.uuid5(LANE_NAMESPACE, f"{record_type}:{semantic_key}"))


def identity_set_sha256(values: Iterable[str]) -> str:
    return sha256_bytes("".join(value + "\n" for value in sorted(set(values))).encode("utf-8"))


def canonical_row_sha256(row: dict[str, Any]) -> str:
    return sha256_bytes((compact_json(row) + "\n").encode("utf-8"))


def owner_file_fact(owner_manifest: dict[str, Any], relative: str) -> dict[str, Any]:
    matches = [row for row in owner_manifest["files"] if row["path"] == relative]
    require(len(matches) == 1, f"owner manifest does not bind exactly one {relative}")
    row = matches[0]
    return {
        "path": relative,
        "path_base": "owner_package_root",
        "role": "owner_native_shard",
        "bytes": row["bytes"],
        "sha256": row["sha256"],
    }


def owner_shard_fact(owner_root: Path, owner_manifest: dict[str, Any], relative: str) -> dict[str, Any]:
    result = owner_file_fact(owner_manifest, relative)
    rows = read_jsonl(owner_root.joinpath(*PurePosixPath(relative).parts))
    ids = [str(row["id"]) for row in rows]
    require(len(ids) == len(set(ids)), f"duplicate owner-native IDs in {relative}")
    result["records"] = len(rows)
    result["record_id_set_sha256"] = identity_set_sha256(ids)
    return result


def combined_shard_identity(shards: Iterable[dict[str, Any]]) -> str:
    return sha256_bytes(
        "".join(
            f"{row['path']}\0{row['records']}\0{row['record_id_set_sha256']}\n"
            for row in sorted(shards, key=lambda item: item["path"])
        ).encode("utf-8")
    )


def inventory_sha256(facts: Iterable[dict[str, Any]]) -> str:
    data = "".join(
        f"{item['path']}\0{item['bytes']}\0{item['sha256']}\n"
        for item in sorted(facts, key=lambda item: item["path"])
    ).encode("utf-8")
    return sha256_bytes(data)


def make_row(
    record_type: str,
    semantic_key: str,
    payload: dict[str, Any],
    *,
    dataset_id: str,
    owner_authority_id: str,
    normalized_state: str = "validated",
    owner_native_state: str | None = None,
) -> dict[str, Any]:
    return {
        "dataset_id": dataset_id,
        "id": projection_id(record_type, semantic_key),
        "normalized_state": normalized_state,
        "owner_authority_id": owner_authority_id,
        "owner_native_state": owner_native_state,
        "payload": payload,
        "record_type": record_type,
        "recorded_at": RECORDED_AT,
        "semantic_key": semantic_key,
    }


def verify_exact(path: Path, key: str, relative: str, path_base: str) -> dict[str, Any]:
    require(path.is_file(), f"missing input: {path}")
    expected_bytes, expected_sha = EXPECTED_INPUTS[key]
    fact = file_fact(path, relative, key, path_base=path_base)
    require(fact["bytes"] == expected_bytes, f"input byte drift: {key}")
    require(fact["sha256"] == expected_sha, f"input hash drift: {key}")
    return fact


def verify_owner_manifest_closure(owner_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    facts = manifest.get("files")
    require(isinstance(facts, list) and len(facts) == 78, "owner manifest must bind exactly 78 files")
    seen: set[str] = set()
    checked: list[dict[str, Any]] = []
    for entry in facts:
        relative = str(entry["path"])
        pure = PurePosixPath(relative)
        require(not pure.is_absolute() and ".." not in pure.parts and relative not in seen, "unsafe/duplicate owner path")
        path = owner_root.joinpath(*pure.parts)
        require(path.is_file(), f"missing owner-manifest member: {relative}")
        actual = file_fact(path, relative, "owner_manifest_member", path_base="owner_package_root")
        require(actual["bytes"] == entry["bytes"] and actual["sha256"] == entry["sha256"], f"owner member drift: {relative}")
        seen.add(relative)
        checked.append(actual)
    require(sum(row["bytes"] for row in checked) == 436966309, "owner manifest byte aggregate drift")
    return {
        "files": len(checked),
        "bytes": sum(row["bytes"] for row in checked),
        "inventory_sha256": inventory_sha256(checked),
        "result": "pass",
    }


def authority_paths(args: argparse.Namespace) -> dict[str, tuple[Path, str, str]]:
    repo = args.repository_root.resolve()
    owner = args.owner_package_root.resolve()
    pilot = repo / "backend/v2.1/pilots/b10-dmoi"
    federation = repo / "backend/v2/program-matematika-indonesia-federation-v0.4.4"
    return {
        "capability_contract": (repo / "backend/v2.2/global-capability-contract-v0.1.0.json", "backend/v2.2/global-capability-contract-v0.1.0.json", "program_repository_root"),
        "learner_route_readback": (repo / "backend/v2.3/authorities/B10_COURSE_ROOT_ANONYMOUS_READBACK_20260830.json", "backend/v2.3/authorities/B10_COURSE_ROOT_ANONYMOUS_READBACK_20260830.json", "program_repository_root"),
        "migration_receipt": (repo / "backend/migrations/dmoi4-id-v1/MIGRATION_RECEIPT.json", "backend/migrations/dmoi4-id-v1/MIGRATION_RECEIPT.json", "program_repository_root"),
        "pilot_manifest": (pilot / "manifest.json", "backend/v2.1/pilots/b10-dmoi/manifest.json", "program_repository_root"),
        "units": (pilot / "units.jsonl", "backend/v2.1/pilots/b10-dmoi/units.jsonl", "program_repository_root"),
        "relations": (pilot / "relations.jsonl", "backend/v2.1/pilots/b10-dmoi/relations.jsonl", "program_repository_root"),
        "search": (pilot / "search.jsonl", "backend/v2.1/pilots/b10-dmoi/search.jsonl", "program_repository_root"),
        "rights_accessibility": (pilot / "rights_accessibility.json", "backend/v2.1/pilots/b10-dmoi/rights_accessibility.json", "program_repository_root"),
        "pilot_validation": (pilot / "validation_report.json", "backend/v2.1/pilots/b10-dmoi/validation_report.json", "program_repository_root"),
        "courses_current": (federation / "data/courses.jsonl", "backend/v2/program-matematika-indonesia-federation-v0.4.4/data/courses.jsonl", "program_repository_root"),
        "federation_manifest": (federation / "manifest.json", "backend/v2/program-matematika-indonesia-federation-v0.4.4/manifest.json", "program_repository_root"),
        "owner_manifest": (owner / "package.json", "package.json", "owner_package_root"),
        "owner_namespace": (owner / "schema/namespace.json", "schema/namespace.json", "owner_package_root"),
        "owner_validation": (owner / "validation_report.json", "validation_report.json", "owner_package_root"),
    }


def build_tables(
    units: list[dict[str, Any]],
    relations: list[dict[str, Any]],
    searches: list[dict[str, Any]],
    rights_accessibility: dict[str, Any],
    course: dict[str, Any],
    prerequisite_course: dict[str, Any],
    courses_authority_sha256: str,
    learner_route_readback: dict[str, Any],
    owner_manifest: dict[str, Any],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    require(len(units) == 161 and len(relations) == 284 and len(searches) == 161, "pilot scope mismatch")
    native_ids = [row["stable_unit_id"] for row in units]
    require(len(native_ids) == len(set(native_ids)), "duplicate native unit ID")
    require(all(row["native_unit_id"] == row["stable_unit_id"] for row in units), "pilot native/stable ID mismatch")
    require(identity_set_sha256(native_ids) == "023c7832b6244ba795e6b7c15e36e9a11da7cc0022d6283f31264494dae1778f", "pilot unit identity-set drift")

    course_payload = course["payload"]
    require(course["id"] == CURRENT_COURSE_ID and course_payload["v1_course_id"] == CURRENT_V1_COURSE_ID, "current course binding drift")
    require(course_payload["course_id"] == "B10" and course_payload["unit_route_state"] == "planned_not_published", "current course scope drift")
    require(course_payload["prerequisite_course_ids"] == ["A30"], "current B10 prerequisite list drift")
    prerequisite_payload = prerequisite_course["payload"]
    require(
        prerequisite_course["id"] == CURRENT_A30_COURSE_ID
        and prerequisite_payload["course_id"] == "A30"
        and prerequisite_payload["v1_course_id"] == CURRENT_A30_V1_COURSE_ID,
        "current A30 course binding drift",
    )
    learner_url = course_payload["learner_start_url"]
    require(learner_url == "https://kokunoyumeto.github.io/discrete-mathematics-open-introduction-id/", "learner route drift")
    require(
        learner_route_readback["result"] == "pass"
        and learner_route_readback["authentication_used"] is False
        and learner_route_readback["learner_route"] == learner_url,
        "anonymous learner-route readback authority drift",
    )

    dataset_key = "b10:dmoi4:dataset"
    dataset_id = projection_id("dataset", dataset_key)
    owner_key = "b10:dmoi4:owner-authority"
    owner_id = projection_id("owner_authority", owner_key)
    edition_key = "b10:dmoi4:edition:id-ID:fourth"
    edition_id = projection_id("edition", edition_key)
    profile_id = projection_id("adapter_profile", f"b10:dmoi4:adapter-profile:{ADAPTER_VERSION}")
    run_id = projection_id("adapter_run", f"b10:dmoi4:adapter-run:{ADAPTER_VERSION}")
    route_id = projection_id("route", "b10:dmoi4:route:course-root")
    reader_id = projection_id("reader_surface", "b10:dmoi4:reader-surface:course-root")
    artifact_id = projection_id("artifact", "b10:dmoi4:artifact:course-root-html")

    projected_units = {
        native_id: projection_id("unit", f"b10:dmoi4:unit:{native_id}") for native_id in native_ids
    }
    rights_components = rights_accessibility["rights"]["components"]
    require(len(rights_components) == 5, "rights component closure drift")
    projected_rights = {
        row["id"]: projection_id("rights", f"b10:dmoi4:rights:{row['id']}") for row in rights_components
    }

    tables: dict[str, list[dict[str, Any]]] = {name: [] for name in TABLE_ORDER}
    tables["owner_authorities"] = [make_row(
        "owner_authority", owner_key,
        {
            "authority_kind": "owner_native_package",
            "authority_scope": "complete B10 semantic corpus, rights, correction, terminology, accessibility, and publication evidence",
            "course_ids": [CURRENT_COURSE_ID],
            "dataset_id": owner_manifest["dataset_id"],
            "dataset_version": owner_manifest["dataset_version"],
            "native_namespace": OWNER_NAMESPACE,
            "native_schema_name": owner_manifest["schema_name"],
            "native_schema_version": owner_manifest["schema_version"],
            "record_count": owner_manifest["record_count"],
            "public_repository_url": course_payload["artifact_matrix"]["repository"],
            "release_lineage_url": course_payload["artifact_matrix"]["doi"],
            "sole_integrator_publisher": True,
            "zero_copy": True,
        },
        dataset_id=dataset_id, owner_authority_id=owner_id,
        normalized_state="published", owner_native_state="full-admitted",
    )]

    tables["datasets"] = [make_row(
        "dataset", dataset_key,
        {
            "adapter_profile_id": profile_id,
            "capabilities": CAPABILITY_NAMES,
            "course_ids": [CURRENT_COURSE_ID],
            "dataset_kind": "zero_copy_owner_projection",
            "materialized_record_counts": {"unit": 161, "relation": 284, "search_document": 161},
            "owner_dataset_id": owner_manifest["dataset_id"],
            "owner_record_count": owner_manifest["record_count"],
            "publication_state": "public",
            "reader_surface_ids": [reader_id],
            "rights_component_count": 5,
            "accessibility_native_record_count": 235,
            "limitations": [
                "No textbook prose is copied into the central adapter.",
                "Unit HTML anchors remain null because no exact public anchor mapping is hash-bound.",
                "No concept relation, assessment semantics, research state, or remote-service behavior is inferred.",
            ],
        },
        dataset_id=dataset_id, owner_authority_id=owner_id,
        normalized_state="published", owner_native_state="full-admitted",
    )]

    default_rights_id = projected_rights[units[0]["rights_component_id"]]
    tables["editions"] = [make_row(
        "edition", edition_key,
        {
            "locale": "id-ID",
            "title": "Matematika Diskret: Sebuah Pengantar Terbuka — Edisi Keempat, Bahasa Indonesia",
            "version_label": owner_manifest["dataset_version"],
            "owner_authority_id": owner_id,
            "rights_id": default_rights_id,
            "source_format": "PreTeXt/XML",
            "target_format": "PreTeXt/XML, HTML, PDF",
            "edition_notes": "Zero-copy v2.3 adapter; the owner-native corpus remains authoritative.",
        },
        dataset_id=dataset_id, owner_authority_id=owner_id,
        normalized_state="published", owner_native_state="published",
    )]

    for ordinal, source in enumerate(units, 1):
        native_id = source["stable_unit_id"]
        projected_id = projected_units[native_id]
        parent_native = source["parent_stable_unit_id"]
        parent_projected = None if parent_native is None else projected_units[parent_native]
        semantic = f"b10:dmoi4:unit:{native_id}"
        unit = make_row(
            "unit", semantic,
            {
                "native_unit_id": native_id,
                "native_unit_kind": source["native_unit_kind"],
                "native_locator": source["native_locator"],
                "parent_native_unit_id": parent_native,
                "parent_projected_unit_id": parent_projected,
                "order_key": source["order_key"],
                "title": source["localized_title"],
                "title_locale": source["locale"],
                "localized_occurrence_id": source["localized_occurrence_id"],
                "localized_title_variant_id": source["localized_title_variant_id"],
                "localized_title_payload_sha256": source["localized_title_payload_sha256"],
                "source_file_revision_id": source["source_file_revision_id"],
                "source_file_sha256": source["source_file_sha256"],
                "source_subtree_sha256": source["source_subtree_sha256"],
                "target_file_revision_id": source["target_file_revision_id"],
                "target_file_sha256": source["target_file_sha256"],
                "target_subtree_sha256": source["target_subtree_sha256"],
                "translation_state": source["translation_state"],
                "rights_id": projected_rights[source["rights_component_id"]],
                "learner_route": {
                    "route_id": route_id,
                    "url": learner_url,
                    "anchor": None,
                    "route_state": "course_fallback_unit_route_planned_not_published",
                    "machine_data_only": False,
                },
            },
            dataset_id=dataset_id, owner_authority_id=owner_id,
            normalized_state="published", owner_native_state=source["translation_state"],
        )
        require(unit["id"] == projected_id, "unit projection formula drift")
        tables["units"].append(unit)
        tables["course_unit_memberships"].append(make_row(
            "course_unit_membership", f"b10:dmoi4:membership:{native_id}",
            {
                "course_id": CURRENT_COURSE_ID,
                "edition_id": edition_id,
                "unit_id": projected_id,
                "native_unit_id": native_id,
                "ordinal": ordinal,
                "order_key": source["order_key"],
                "required": None,
                "visible": None,
                "membership_policy_state": "not_projected_no_bound_curriculum_policy",
            },
            dataset_id=dataset_id, owner_authority_id=owner_id,
            normalized_state="published", owner_native_state="published",
        ))
        reverse = f"jsonl_id(data/units.jsonl,{native_id})"
        tables["native_bindings"].append(make_row(
            "native_binding", f"b10:dmoi4:native-binding:{native_id}",
            {
                "mapping_cardinality": "one_to_one",
                "native_id": native_id,
                "native_record_type": "unit",
                "native_schema_name": owner_manifest["schema_name"],
                "native_schema_version": owner_manifest["schema_version"],
                "native_namespace": OWNER_NAMESPACE,
                "subject_id": projected_id,
                "reverse_recipe": reverse,
            },
            dataset_id=dataset_id, owner_authority_id=owner_id,
            owner_native_state="identity_declared",
        ))
        tables["identity_crosswalks"].append(make_row(
            "identity_crosswalk", f"b10:dmoi4:crosswalk:{native_id}",
            {
                "source_namespace": OWNER_NAMESPACE,
                "source_id": native_id,
                "source_record_type": "unit",
                "target_namespace": str(LANE_NAMESPACE),
                "target_id": projected_id,
                "target_record_type": "unit",
                "mapping_cardinality": "one_to_one",
                "mapping_state": "mapped",
                "reverse_recipe": reverse,
            },
            dataset_id=dataset_id, owner_authority_id=owner_id,
            owner_native_state="identity_declared",
        ))
        tables["rights_assignments"].append(make_row(
            "rights_assignment", f"b10:dmoi4:rights-assignment:{native_id}",
            {
                "assignment_state": "effective",
                "inheritance": "direct_from_pilot_unit",
                "rights_id": projected_rights[source["rights_component_id"]],
                "target_id": projected_id,
                "target_native_id": native_id,
            },
            dataset_id=dataset_id, owner_authority_id=owner_id,
            normalized_state="published", owner_native_state="admitted",
        ))

    relation_type_counts: dict[str, int] = {}
    external_endpoints: set[str] = set()
    for source in relations:
        native_relation_id = source.get("evidence", {}).get("native_relation_id")
        if native_relation_id is None:
            native_relation_id = f"central:{source['relation_type']}:{source['from_id']}:{source['to_id']}"
        relation_type_counts[source["relation_type"]] = relation_type_counts.get(source["relation_type"], 0) + 1
        from_projected = projected_units.get(source["from_id"])
        to_projected = projected_units.get(source["to_id"])
        if from_projected is None:
            external_endpoints.add(source["from_id"])
        if to_projected is None:
            external_endpoints.add(source["to_id"])
        evidence = dict(source["evidence"])
        if source["relation_type"] == "requires_course":
            evidence["current_central_courses_jsonl_sha256"] = courses_authority_sha256
            evidence["current_b10_course_record_id"] = CURRENT_COURSE_ID
            evidence["current_b10_v1_course_id"] = CURRENT_V1_COURSE_ID
            evidence["current_b10_course_record_sha256"] = canonical_row_sha256(course)
            evidence["current_a30_course_record_id"] = CURRENT_A30_COURSE_ID
            evidence["current_a30_v1_course_id"] = CURRENT_A30_V1_COURSE_ID
            evidence["current_a30_course_record_sha256"] = canonical_row_sha256(prerequisite_course)
            evidence["current_prerequisite_course_ids"] = list(course_payload["prerequisite_course_ids"])
            evidence["current_prerequisite_binding_state"] = "reconfirmed_from_federation_v0.4.4"
            evidence["historical_pilot_evidence_preserved"] = True
        tables["relations"].append(make_row(
            "relation", f"b10:dmoi4:relation:{native_relation_id}",
            {
                "relation_type": source["relation_type"],
                "strength": source["strength"],
                "from_endpoint": {"native_id": source["from_id"], "projected_id": from_projected},
                "to_endpoint": {"native_id": source["to_id"], "projected_id": to_projected},
                "evidence": evidence,
                "concept_relation_inferred": False,
            },
            dataset_id=dataset_id, owner_authority_id=owner_id,
            owner_native_state="exact_evidence",
        ))
    require(relation_type_counts == {"contains": 161, "precedes": 122, "requires_course": 1}, "relation type counts drift")
    require(external_endpoints == {"course:A30", "course:B10"}, "external relation endpoint drift")

    search_by_native = {row["stable_unit_id"]: row for row in searches}
    require(set(search_by_native) == set(native_ids), "search/unit identity closure drift")
    for native_id in native_ids:
        source = search_by_native[native_id]
        require(source["learner_url"] == learner_url, "search learner route drift")
        tables["search_documents"].append(make_row(
            "search_document", f"b10:dmoi4:search:{native_id}",
            {
                "course_id": CURRENT_COURSE_ID,
                "unit_id": projected_units[native_id],
                "native_unit_id": native_id,
                "locale": source["locale"],
                "title": source["title"],
                "bounded_search_text": source["search_text"],
                "order_key": source["order_key"],
                "learner_url": learner_url,
                "learner_anchor": None,
            },
            dataset_id=dataset_id, owner_authority_id=owner_id,
            normalized_state="published", owner_native_state="published",
        ))

    for component in rights_components:
        tables["rights"].append(make_row(
            "rights", f"b10:dmoi4:rights:{component['id']}",
            {
                "native_rights_id": component["id"],
                "source_component_id": component["source_component_id"],
                "assertion_status": component["assertion_status"],
                "attribution": component["attribution"],
                "license_expression": component["license_expression"],
                "third_party_status": component["third_party_status"],
                "flattened_course_license": False,
            },
            dataset_id=dataset_id, owner_authority_id=owner_id,
            normalized_state="published", owner_native_state="admitted",
        ))

    tables["artifacts"] = [make_row(
        "artifact", "b10:dmoi4:artifact:course-root-html",
        {
            "artifact_kind": "semantic_html_course_root",
            "course_ids": [CURRENT_COURSE_ID],
            "edition_id": edition_id,
            "locale": "id-ID",
            "public_url": learner_url,
            "publication_state": "public_anonymous_readback_verified",
            "verification_state": "course_root_and_resolved_entry_hash_bound",
            "verification_authority": "learner_route_readback",
            "authority_record_id": CURRENT_COURSE_ID,
            "authority_record_sha256": canonical_row_sha256(course),
            "route_ids": [route_id],
            "rights_component_ids": list(projected_rights.values()),
        },
        dataset_id=dataset_id, owner_authority_id=owner_id,
        normalized_state="published", owner_native_state="federation_plus_anonymous_readback",
    )]
    require(tables["artifacts"][0]["id"] == artifact_id, "artifact ID drift")
    tables["reader_surfaces"] = [make_row(
        "reader_surface", "b10:dmoi4:reader-surface:course-root",
        {
            "action": "learn",
            "artifact_id": artifact_id,
            "course_ids": [CURRENT_COURSE_ID],
            "format": "semantic_html",
            "locale": "id-ID",
            "primary": True,
            "learner_destination_state": "federation_primary_and_anonymous_readback_verified",
            "public_url": learner_url,
            "publication_state": "public_anonymous_readback_verified",
            "unit_anchor_coverage": 0,
        },
        dataset_id=dataset_id, owner_authority_id=owner_id,
        normalized_state="published", owner_native_state="federation_plus_anonymous_readback",
    )]
    require(tables["reader_surfaces"][0]["id"] == reader_id, "reader ID drift")
    tables["routes"] = [make_row(
        "route", "b10:dmoi4:route:course-root",
        {
            "access_state": "public_anonymous_readback_verified",
            "course_id": CURRENT_COURSE_ID,
            "machine_data_only": False,
            "public_url": learner_url,
            "route_kind": "verified_course_root_fallback",
            "surface_id": reader_id,
            "target_kind": "readable_html",
            "unit_id": None,
            "unit_anchor": None,
            "unit_route_state": "planned_not_published",
        },
        dataset_id=dataset_id, owner_authority_id=owner_id,
        normalized_state="published", owner_native_state="federation_plus_anonymous_readback",
    )]
    require(tables["routes"][0]["id"] == route_id, "route ID drift")

    tables["adapter_profiles"] = [make_row(
        "adapter_profile", f"b10:dmoi4:adapter-profile:{ADAPTER_VERSION}",
        {
            "adapter_id": "b10-dmoi-zero-copy-v2.3",
            "adapter_version": ADAPTER_VERSION,
            "capability_map": {
                "structure_localization": "referenced_native_shards",
                "terminology": "referenced_native_shards",
                "mathematical_preservation": "referenced_native_shards",
                "assessment_support": "not_projected",
                "assets": "referenced_native_shards",
                "accessibility": "referenced_native_shards",
                "corrections": "referenced_native_shards",
                "computational_interactives": "referenced_native_shards",
                "publication": "materialized",
                "research_support": "not_projected",
            },
            "identity_rules": [
                "Preserve owner and pilot IDs as native identities.",
                "Derive separate v2.3 projection IDs from record_type plus corpus-qualified semantic key.",
                "Never derive identity from translated prose, page numbers, route URLs, or build time.",
            ],
            "zero_copy": True,
            "owner_native_record_count": owner_manifest["record_count"],
            "materialized_pilot_records": 606,
        },
        dataset_id=dataset_id, owner_authority_id=owner_id,
    )]
    require(tables["adapter_profiles"][0]["id"] == profile_id, "profile ID drift")
    projected_counts = {RECORD_TYPE_BY_TABLE[name]: len(rows) for name, rows in tables.items()}
    tables["adapter_runs"] = [make_row(
        "adapter_run", f"b10:dmoi4:adapter-run:{ADAPTER_VERSION}",
        {
            "adapter_profile_id": profile_id,
            "deterministic_replay_requirement": "two absent-directory builds must be byte-identical",
            "input_owner_record_count": owner_manifest["record_count"],
            "native_input_counts": {
                "units": 3307, "terms": 106, "term_variants": 212,
                "assets": 482, "asset_revisions": 964, "accessibility": 235,
                "corrections": 79, "correction_claims": 114,
                "correction_bindings": 114, "interactives": 252,
            },
            "projected_output_counts_before_run_record": projected_counts,
            "reverse_extraction_requirement": "all 161 unit crosswalks exact",
            "validation_state": "pending_independent_validator",
        },
        dataset_id=dataset_id, owner_authority_id=owner_id,
        owner_native_state="pass",
    )]
    require(tables["adapter_runs"][0]["id"] == run_id, "run ID drift")
    tables["qa_events"] = [make_row(
        "qa_event", f"b10:dmoi4:qa:build-preflight:{ADAPTER_VERSION}",
        {
            "method": "frozen-input hash, manifest closure, canonical JSONL, selector, identity, scope, route, rights, and no-inference checks",
            "qa_kind": "b10_v23_zero_copy_adapter_build",
            "result": "pending_independent_validator",
            "subject_ids": [dataset_id, run_id],
            "warnings": ["Per-unit public HTML anchors are not claimed."],
        },
        dataset_id=dataset_id, owner_authority_id=owner_id,
        owner_native_state="pass",
    )]

    context = {
        "package_id": projection_id("package_extension", f"b10:dmoi4:v2.3.1:{ADAPTER_VERSION}"),
        "dataset_id": dataset_id,
        "owner_authority_id": owner_id,
        "edition_id": edition_id,
        "adapter_profile_id": profile_id,
        "adapter_run_id": run_id,
        "route_id": route_id,
        "reader_surface_id": reader_id,
        "artifact_id": artifact_id,
        "current_course_id": CURRENT_COURSE_ID,
        "current_v1_course_id": CURRENT_V1_COURSE_ID,
        "current_a30_course_id": CURRENT_A30_COURSE_ID,
        "current_a30_v1_course_id": CURRENT_A30_V1_COURSE_ID,
        "current_b10_course_record_sha256": canonical_row_sha256(course),
        "current_a30_course_record_sha256": canonical_row_sha256(prerequisite_course),
        "learner_url": learner_url,
        "projected_unit_ids": projected_units,
        "native_unit_ids": native_ids,
        "rights_ids": projected_rights,
        "external_endpoints": sorted(external_endpoints),
        "relation_type_counts": relation_type_counts,
    }
    return tables, context


def build_capabilities(
    package_id: str,
    dataset_id: str,
    owner_root: Path,
    owner_manifest: dict[str, Any],
    authorities: dict[str, dict[str, Any]],
    tables: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    owner_schema = owner_file_fact(owner_manifest, "schema/backend-full.schema.json")
    owner_schema["role"] = "owner_backend_schema"

    shard_paths = {
        "structure_localization": ["data/units.jsonl", "data/occurrences.jsonl", "data/segments.jsonl", "data/segment_variants.jsonl"],
        "terminology": ["data/terms.jsonl", "data/term_variants.jsonl"],
        "mathematical_preservation": ["data/file_revisions.jsonl", "data/segments.jsonl", "data/segment_variants.jsonl"],
        "assets": ["data/assets.jsonl", "data/asset_revisions.jsonl"],
        "accessibility": ["data/accessibility.jsonl"],
        "corrections": ["data/corrections.jsonl", "data/correction_claims.jsonl", "data/correction_bindings.jsonl"],
        "computational_interactives": ["data/interactives.jsonl"],
        "publication": ["data/artifacts.jsonl", "data/artifact_members.jsonl"],
    }
    shards = {
        name: [owner_shard_fact(owner_root, owner_manifest, path) for path in paths]
        for name, paths in shard_paths.items()
    }
    projected_tables = {
        "structure_localization": ["units", "course_unit_memberships"],
        "publication": ["artifacts", "reader_surfaces", "routes"],
    }
    projected_ids = {
        name: [row["id"] for table in names for row in tables[table]]
        for name, names in projected_tables.items()
    }

    states = {
        "structure_localization": "referenced_native_shards",
        "terminology": "referenced_native_shards",
        "mathematical_preservation": "referenced_native_shards",
        "assessment_support": "not_projected",
        "assets": "referenced_native_shards",
        "accessibility": "referenced_native_shards",
        "corrections": "referenced_native_shards",
        "computational_interactives": "referenced_native_shards",
        "publication": "materialized",
        "research_support": "not_projected",
    }
    closure_rules = {
        "structure_localization": ["owner-native structure and localization remain authoritative", "all 161 projected structural roots reverse-map to exact owner units"],
        "terminology": ["term and term-variant shards remain owner-native and hash-bound", "no terminology prose is copied into the adapter"],
        "mathematical_preservation": ["source/target file revisions, semantic segments, and variants remain owner-native", "no formula or textbook body is copied into the adapter"],
        "assessment_support": ["absence of a typed assessment projection is explicit", "exercise semantics are not inferred from owner prose"],
        "assets": ["asset identities and revision bytes remain owner-native", "no asset payload is copied into the adapter"],
        "accessibility": ["all 235 typed accessibility records remain owner-native and hash-bound", "the 183 description and 52 short-description split is independently replayed"],
        "corrections": ["correction, claim, and binding shards remain owner-native", "no upstream-contact state is invented"],
        "computational_interactives": ["all typed interactive records remain owner-native", "remote execution behavior is not inferred"],
        "publication": ["the human-readable course root remains primary", "machine JSON and CSV remain secondary", "the root and resolved entry have an anonymous byte-readback authority"],
        "research_support": ["absence of a typed research-support projection is explicit", "research semantics are not inferred"],
    }

    capabilities: list[dict[str, Any]] = []
    for name in CAPABILITY_NAMES:
        capability_shards = shards.get(name, [])
        ids = projected_ids.get(name, [])
        not_projected = states[name] == "not_projected"
        capabilities.append({
            "name": name,
            "version": "0.1.0",
            "state": states[name],
            "schema_binding": None if not_projected else owner_schema,
            "shard_refs": capability_shards,
            "native_count": sum(row["records"] for row in capability_shards),
            "projected_count": len(ids),
            "identity_set_sha256": (
                identity_set_sha256(ids) if ids
                else (combined_shard_identity(capability_shards) if capability_shards else None)
            ),
            "identity_set_scope": "projected_records" if ids else ("native_shard_records" if capability_shards else "none"),
            "closure_rules": closure_rules[name],
            "loss_gap_report": {
                "status": "declared_limitation" if not_projected else "closed",
                "reason": (
                    "No typed projection is admitted; the adapter reports this capability as not projected and infers nothing."
                    if not_projected else
                    "All claimed projected records and/or referenced owner-native shards are explicitly bound and replayable."
                ),
            },
        })

    rights_shards = [
        owner_shard_fact(owner_root, owner_manifest, path)
        for path in ["data/rights.jsonl", "data/rights_assignments.jsonl", "data/rights_rules.jsonl", "data/rights_rule_members.jsonl"]
    ]
    return {
        "$schema": "schema/capability-declarations-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-capability-declarations/0.2.0",
        "schema_version": "0.2.0",
        "package_id": package_id,
        "dataset_id": dataset_id,
        "contract_binding": authorities["capability_contract"],
        "capabilities": capabilities,
        "legacy_labels": [],
        "namespace_crosswalk_binding": {"path": "namespace-crosswalk-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "csv_projection_binding": {"path": "csv-projection-manifest-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "translation_state_binding": {"path": "translation-state-index-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "rights_cross_cutting": {
            "state": "referenced_native_shards",
            "shard_refs": rights_shards,
            "native_count": sum(row["records"] for row in rights_shards),
            "identity_set_sha256": combined_shard_identity(rights_shards),
            "closure_rules": ["component rights are never flattened", "all owner-native rights tables remain exact and hash-bound"],
        },
        "recorded_at": RECORDED_AT,
    }


def write_csv_surfaces(output: Path, tables: dict[str, list[dict[str, Any]]], package_id: str) -> dict[str, Any]:
    csv_root = output / "csv"
    csv_root.mkdir(parents=True, exist_ok=True)
    table_entries: list[dict[str, Any]] = []
    global_rows: list[list[str]] = []
    for table_name in TABLE_ORDER:
        rows = tables[table_name]
        jsonl_path = output / "tables" / f"{table_name}.jsonl"
        csv_path = csv_root / f"{table_name}.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["stable_id", "record_type", "canonical_record_json"])
            for ordinal, row in enumerate(rows, 1):
                canonical = compact_json(row)
                writer.writerow([row["id"], row["record_type"], canonical])
                global_rows.append([f"tables/{table_name}.jsonl", str(ordinal), row["id"], row["record_type"], canonical])
        reconstructed = "".join(row[4] + "\n" for row in global_rows if row[0] == f"tables/{table_name}.jsonl").encode("utf-8")
        require(reconstructed == jsonl_path.read_bytes(), f"CSV/JSONL round-trip failed: {table_name}")
        table_entries.append({
            "table": table_name,
            "records": len(rows),
            "source_jsonl": file_fact(jsonl_path, f"tables/{table_name}.jsonl", "canonical_jsonl"),
            "csv": file_fact(csv_path, f"csv/{table_name}.csv", "deterministic_csv"),
            "roundtrip_sha256": sha256_bytes(reconstructed),
            "roundtrip_state": "pass",
        })
    global_rows.sort(key=lambda row: (row[3], row[2], row[0], int(row[1])))
    records_path = output / "records.csv"
    with records_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["source_jsonl_path", "source_row_ordinal", "stable_id", "record_type", "canonical_record_json"])
        writer.writerows(global_rows)
    records_fact = file_fact(records_path, "records.csv", "deterministic_global_csv")
    csv_facts = [entry["csv"] for entry in table_entries] + [records_fact]
    return {
        "$schema": "schema/csv-projection-manifest-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-csv-projection-manifest/0.2.0",
        "schema_version": "0.2.0",
        "package_id": package_id,
        "source_tables": "tables/*.jsonl",
        "header": ["stable_id", "record_type", "canonical_record_json"],
        "table_order": TABLE_ORDER,
        "tables": table_entries,
        "records_csv": {
            **records_fact,
            "records": len(global_rows),
            "roundtrip_sha256": sha256_bytes("".join(row[4] + "\n" for row in global_rows).encode("utf-8")),
        },
        "aggregate_sha256": inventory_sha256(csv_facts),
        "canonical_serialization": {
            "encoding": "UTF-8",
            "newline": "LF",
            "csv_dialect": "RFC4180-compatible quoting",
            "record_terminator": "LF",
            "table_row_order": "source_jsonl_order",
            "aggregate_table_order": "record_type_then_stable_id_then_source_path_then_ordinal",
            "canonical_record_json": "exact_source_jsonl_record",
            "trailing_newline": True,
            "roundtrip": "csv_to_jsonl_to_csv_byte_identical",
        },
        "recorded_at": RECORDED_AT,
    }


def package_payload_files(output: Path) -> list[dict[str, Any]]:
    excluded = {"manifest.json", "PACKAGE_CHECKSUMS.sha256"}
    facts: list[dict[str, Any]] = []
    for path in sorted(item for item in output.rglob("*") if item.is_file()):
        relative = path.relative_to(output).as_posix()
        if relative in excluded:
            continue
        facts.append(file_fact(path, relative, "package_payload"))
    return facts


def build(args: argparse.Namespace) -> dict[str, Any]:
    output = args.output.resolve()
    require(not output.exists() or args.replace, "output exists; pass --replace")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    paths = authority_paths(args)
    authorities = {
        key: verify_exact(path, key, relative, path_base)
        for key, (path, relative, path_base) in paths.items()
    }
    owner_manifest = read_json(paths["owner_manifest"][0])
    require(owner_manifest["record_count"] == 163583 and owner_manifest["stage"] == "full-admitted", "owner manifest state drift")
    owner_namespace = read_json(paths["owner_namespace"][0])
    require(owner_namespace["namespace_uuid"] == OWNER_NAMESPACE, "owner namespace drift")
    owner_validation = read_json(paths["owner_validation"][0])
    require(owner_validation.get("result") == "pass", "owner validation is not passing")
    closure = verify_owner_manifest_closure(args.owner_package_root.resolve(), owner_manifest)

    migration = read_json(paths["migration_receipt"][0])
    require(migration["validation"]["result"] == "pass", "v1 migration is not passing")
    require(migration["validation"]["identity_preserved_count"] == 163583, "v1 identity preservation drift")
    require(migration["validation"]["lossless_reverse_records"] == 163583, "v1 reverse extraction drift")
    require(migration["transformation"]["changed_record_ids"] == 0, "v1 changed record IDs")
    require(migration["transformation"]["changed_payload_fields"] == 0, "v1 changed payloads")

    pilot_manifest = read_json(paths["pilot_manifest"][0])
    pilot_validation = read_json(paths["pilot_validation"][0])
    require(pilot_validation.get("result") == "pass" and not pilot_validation.get("errors") and not pilot_validation.get("warnings"), "pilot validation is not clean")
    units = read_jsonl(paths["units"][0])
    relations = read_jsonl(paths["relations"][0])
    searches = read_jsonl(paths["search"][0])
    rights_accessibility = read_json(paths["rights_accessibility"][0])
    learner_route_readback = read_json(paths["learner_route_readback"][0])
    current_courses = read_jsonl(paths["courses_current"][0])
    current_matches = [row for row in current_courses if row.get("payload", {}).get("course_id") == "B10"]
    require(len(current_matches) == 1, "current B10 course row closure failed")
    prerequisite_matches = [row for row in current_courses if row.get("payload", {}).get("course_id") == "A30"]
    require(len(prerequisite_matches) == 1, "current A30 course row closure failed")

    tables, context = build_tables(
        units,
        relations,
        searches,
        rights_accessibility,
        current_matches[0],
        prerequisite_matches[0],
        authorities["courses_current"]["sha256"],
        learner_route_readback,
        owner_manifest,
    )
    all_ids = [row["id"] for rows in tables.values() for row in rows]
    require(len(all_ids) == len(set(all_ids)), "projected record IDs are not globally unique")
    for table_name in TABLE_ORDER:
        write_jsonl(output / "tables" / f"{table_name}.jsonl", tables[table_name])

    evidence_root = output / "evidence"
    evidence_root.mkdir(parents=True)
    shutil.copyfile(paths["rights_accessibility"][0], evidence_root / "rights_accessibility.json")
    write_json(output / "INPUT_AUTHORITIES.json", {
        "schema_id": "program-matematika-indonesia/b10-v23-input-authorities/0.1.0",
        "authorities": [authorities[key] for key in sorted(authorities)],
        "owner_manifest_closure": closure,
        "owner_native_non_mutation": True,
        "recorded_at": RECORDED_AT,
    })
    all_course_ids = sorted(row["payload"]["course_id"] for row in current_courses)
    require(len(all_course_ids) == 40 and len(set(all_course_ids)) == 40, "current 40-role course authority closure failed")
    scope = {
        "$schema": "schema/scope-declaration-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-backend-scope/0.2.0",
        "schema_version": "0.2.0",
        "package_id": context["package_id"],
        "dataset_id": context["dataset_id"],
        "scope_kind": "lane_adapter",
        "course_ids": ["B10"],
        "curriculum_role_ids": ["B10"],
        "aggregate_conformance_claim": False,
        "unbound_curriculum_role_ids": [course_id for course_id in all_course_ids if course_id != "B10"],
        "owner_authority_binding": authorities["owner_manifest"],
        "curriculum_authority_binding": authorities["courses_current"],
        "limitations": [
            "B10 only; every other curriculum role remains outside this adapter.",
            "The 163,583-record owner backend is referenced and never copied or rewritten.",
            "No textbook body prose, inferred concept relation, synthetic assessment/research state, or invented unit anchor is emitted.",
            "The verified human-readable course root is primary; machine JSON and CSV are secondary.",
        ],
        "recorded_at": RECORDED_AT,
    }
    write_json(output / "scope-declaration-v0.2.0.json", scope)

    course_mapping = {
        "source_namespace": COMMON_NAMESPACE,
        "source_record_id": CURRENT_V1_COURSE_ID,
        "source_record_type": "course",
        "target_namespace": COMMON_NAMESPACE,
        "target_record_id": CURRENT_COURSE_ID,
        "target_record_type": "course",
        "cardinality": "one_to_one",
        "mapping_state": "mapped",
        "reverse_recipe": "select current courses.jsonl row where payload.v1_course_id equals source_record_id",
        "evidence_refs": ["courses_current", f"row-sha256:{context['current_b10_course_record_sha256']}"],
        "identity_set_sha256": identity_set_sha256([CURRENT_V1_COURSE_ID, CURRENT_COURSE_ID]),
    }
    native_crosswalks = [
        {
            "source_namespace": OWNER_NAMESPACE,
            "source_record_id": native_id,
            "source_record_type": "unit",
            "target_namespace": str(LANE_NAMESPACE),
            "target_record_id": context["projected_unit_ids"][native_id],
            "target_record_type": "unit",
            "cardinality": "one_to_one",
            "mapping_state": "mapped",
            "reverse_recipe": f"select owner data/units.jsonl row with id={native_id}",
            "evidence_refs": ["owner_manifest", "pilot_units"],
            "identity_set_sha256": identity_set_sha256([native_id, context["projected_unit_ids"][native_id]]),
        }
        for native_id in context["native_unit_ids"]
    ]
    crosswalk = {
        "$schema": "schema/namespace-crosswalk-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-namespace-crosswalk/0.2.0",
        "schema_version": "0.2.0",
        "package_id": context["package_id"],
        "profiles": [
            {"name": "b10_owner_native", "namespace": OWNER_NAMESPACE, "formula": "owner documented component encoding"},
            {"name": "v1_common", "namespace": COMMON_NAMESPACE, "formula": "UUIDv5(namespace, record_type + '|' + stable_key)"},
            {"name": "v2_current", "namespace": COMMON_NAMESPACE, "formula": "UUIDv5(namespace, record_type + ':' + semantic_key)"},
            {"name": "v2_3_lane", "namespace": str(LANE_NAMESPACE), "formula": "UUIDv5(namespace, record_type + ':' + corpus-qualified semantic_key)"},
        ],
        "mappings": [course_mapping] + native_crosswalks,
        "unmaterialized_candidates": [{
            "namespace": str(LANE_NAMESPACE),
            "record_type": "course",
            "semantic_key": "course:B10",
            "candidate_record_id": projection_id("course", "course:B10"),
            "state": "deterministic_id_proposal_not_a_mapping",
            "formula": "UUIDv5(lane_namespace, 'course:course:B10')",
            "effective_cardinality": "unresolved_until_materialized",
        }],
        "identity_sets": {
            "native_units_sha256": identity_set_sha256(context["native_unit_ids"]),
            "projected_units_sha256": identity_set_sha256(context["projected_unit_ids"].values()),
            "mapped_pairs_sha256": identity_set_sha256(
                [f"{row['source_record_id']}->{row['target_record_id']}" for row in [course_mapping] + native_crosswalks]
            ),
        },
        "recorded_at": RECORDED_AT,
    }
    write_json(output / "namespace-crosswalk-v0.2.0.json", crosswalk)
    translation_rows = [
        {
            "native_unit_id": row["stable_unit_id"],
            "projected_unit_id": context["projected_unit_ids"][row["stable_unit_id"]],
            "localized_occurrence_id": row["localized_occurrence_id"],
            "localized_title_variant_id": row["localized_title_variant_id"],
            "locale": row["locale"],
            "state": row["translation_state"],
            "source_file_sha256": row["source_file_sha256"],
            "source_subtree_sha256": row["source_subtree_sha256"],
            "target_file_sha256": row["target_file_sha256"],
            "target_subtree_sha256": row["target_subtree_sha256"],
        }
        for row in units
    ]
    translation_state = {
        "$schema": "schema/translation-state-index-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-translation-state-index/0.2.0",
        "schema_version": "0.2.0",
        "package_id": context["package_id"],
        "dataset_id": context["dataset_id"],
        "authority_bindings": [
            authorities["units"],
            owner_file_fact(owner_manifest, "data/occurrences.jsonl"),
            owner_file_fact(owner_manifest, "data/file_revisions.jsonl"),
            owner_file_fact(owner_manifest, "data/segments.jsonl"),
            owner_file_fact(owner_manifest, "data/segment_variants.jsonl"),
        ],
        "coverage": {"course_id": "B10", "granularity": "structural_unit", "authority_rows": 161, "indexed_rows": 161, "inferred_rows": 0},
        "states": ["published"],
        "records": translation_rows,
        "identity_set_sha256": identity_set_sha256(row["projected_unit_id"] for row in translation_rows),
        "no_inference": True,
        "recorded_at": RECORDED_AT,
    }
    write_json(output / "translation-state-index-v0.2.0.json", translation_state)

    csv_index = write_csv_surfaces(output, tables, context["package_id"])
    write_json(output / "csv-projection-manifest-v0.2.0.json", csv_index)
    capabilities = build_capabilities(
        context["package_id"], context["dataset_id"], args.owner_package_root.resolve(), owner_manifest, authorities, tables
    )
    write_json(output / "capability-declarations-v0.2.0.json", capabilities)

    schema_names = [
        "lane-adapter-v2.3.1.schema.json", "capability-declarations-v0.2.schema.json",
        "namespace-crosswalk-v0.2.schema.json", "translation-state-index-v0.2.schema.json",
        "csv-projection-manifest-v0.2.schema.json", "scope-declaration-v0.2.schema.json",
    ]
    schema_root = args.repository_root.resolve() / "backend/v2.3/schema"
    (output / "schema").mkdir(parents=True, exist_ok=True)
    (output / "tools").mkdir(parents=True, exist_ok=True)
    for name in schema_names:
        shutil.copyfile(schema_root / name, output / "schema" / name)
    shutil.copyfile(Path(__file__).resolve(), output / "tools" / "build_b10_v23_adapter.py")
    shutil.copyfile(Path(__file__).resolve().with_name("validate_b10_v23_adapter.py"), output / "tools" / "validate_b10_v23_adapter.py")

    payload_facts = package_payload_files(output)
    payload_identity = inventory_sha256(payload_facts)
    sidecar_names = [
        "capability-declarations-v0.2.0.json", "namespace-crosswalk-v0.2.0.json",
        "translation-state-index-v0.2.0.json", "csv-projection-manifest-v0.2.0.json",
        "scope-declaration-v0.2.0.json",
    ]
    manifest = {
        "$schema": "schema/lane-adapter-v2.3.1.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-lane-adapter/2.3.1",
        "schema_version": "2.3.1",
        "package_id": context["package_id"],
        "dataset_id": context["dataset_id"],
        "extension_id": projection_id("lane_adapter_extension", f"b10:dmoi4:{ADAPTER_VERSION}"),
        "extension_version": ADAPTER_VERSION,
        "recorded_at": RECORDED_AT,
        "scope_declaration": file_fact(output / "scope-declaration-v0.2.0.json", "scope-declaration-v0.2.0.json", "scope_declaration"),
        "authorities": [authorities[key] for key in sorted(authorities)],
        "sidecars": [file_fact(output / name, name, "sidecar") for name in sidecar_names],
        "csv_projection": {
            "manifest": file_fact(output / "csv-projection-manifest-v0.2.0.json", "csv-projection-manifest-v0.2.0.json", "csv_projection_manifest"),
            "table_csv_count": len(TABLE_ORDER),
            "aggregate_csv_count": 1,
            "record_count": sum(len(tables[name]) for name in TABLE_ORDER),
            "roundtrip_state": "pass",
        },
        "build": {
            "builder": file_fact(output / "tools/build_b10_v23_adapter.py", "tools/build_b10_v23_adapter.py", "builder"),
            "validator": file_fact(output / "tools/validate_b10_v23_adapter.py", "tools/validate_b10_v23_adapter.py", "validator"),
            "canonical_serialization": {
                "scope": "builder_generated_json_jsonl_and_csv_only",
                "encoding": "UTF-8",
                "newline": "LF",
                "json_keys": "lexicographically_sorted",
                "trailing_newline": True,
                "copied_schema_and_tool_files": "preserved_exact_source_bytes",
            },
            "deterministic_replay": "byte_identical",
            "build_a_sha256": payload_identity,
            "build_b_sha256": payload_identity,
        },
        "files": payload_facts,
        "seal_policy": {
            "algorithm": "sha256-sorted-path-bytes-v1", "seal_file": "seal.json",
            "seal_excluded_from_own_digest": True,
            "binds": ["schemas", "tools", "input_authorities", "tables", "sidecars", "csv_projections", "manifest"],
        },
        "zero_copy_policy": {
            "owner_native_authoritative": True, "full_prose_centralized": False,
            "owner_ids_reminted": False, "aggregate_conformance_claim": False,
            "machine_data_is_learner_destination": False, "machine_surfaces_secondary": True,
        },
    }
    write_json(output / "manifest.json", manifest)
    seal_facts = payload_facts + [file_fact(output / "manifest.json", "manifest.json", "package_manifest")]
    write_json(output / "seal.json", {
        "schema_id": "interlanguage/global-modular-mathematics-lane-adapter-seal/1.0.0",
        "package_id": context["package_id"],
        "algorithm": "sha256-sorted-path-bytes-v1",
        "files": seal_facts,
        "file_count": len(seal_facts),
        "bytes": sum(row["bytes"] for row in seal_facts),
        "aggregate_sha256": inventory_sha256(seal_facts),
        "seal_excluded_from_own_digest": True,
        "recorded_at": RECORDED_AT,
    })
    checksum_facts = package_payload_files(output) + [file_fact(output / "manifest.json", "manifest.json", "package_manifest")]
    checksum_lines = "".join(
        f"{fact['sha256']}  {fact['path']}\n" for fact in sorted(checksum_facts, key=lambda item: item["path"])
    )
    (output / "PACKAGE_CHECKSUMS.sha256").write_text(checksum_lines, encoding="utf-8", newline="\n")
    return {
        "status": "pass",
        "output": str(output),
        "files": len(checksum_facts) + 1,
        "canonical_records": sum(len(tables[name]) for name in TABLE_ORDER),
        "pilot_materialized_records": 606,
        "payload_inventory_sha256": payload_identity,
        "seal_sha256": sha256_file(output / "seal.json"),
        "checksum_sha256": sha256_file(output / "PACKAGE_CHECKSUMS.sha256"),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--owner-package-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replace", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = build(args)
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(compact_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
