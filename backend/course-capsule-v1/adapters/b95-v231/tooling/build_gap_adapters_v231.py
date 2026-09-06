#!/usr/bin/env python3
"""Build thin, zero-copy v2.3.1 adapters for the remaining gap roles.

This builder deliberately knows nothing about a textbook's prose.  It consumes
one small, hash-bound lane specification and emits the same deterministic
19-table envelope used by the admitted v2.3.1 adapters.  The intended input
roles are A30, B95, and C140; the command refuses any other role so that it
cannot accidentally become a replacement owner builder.

The specification is intentionally evidence-first.  In outline::

    {
      "role_id": "A30",
      "title": "Prakalkulus dan Trigonometri",
      "course_id": "A30",
      "namespace": "7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd",
      "dataset_key": "a30:precalculus-2e:id-ID:v1",
      "owner_namespace": "owner-native-namespace",
      "recorded_at": "2026-09-07T00:00:00Z",
      "authorities": [{"path":"...", "path_base":"owner_package_root",
                       "role":"source_authority", "bytes":1,
                       "sha256":"..."}],
      "curriculum_authority": {"path":"...", "path_base":"program_repository_root",
                                "role":"curriculum_authority", "bytes":1,
                                "sha256":"..."},
      "units": [{"native_id":"...", "ordinal":1, "title":"...",
                 "source_path":"...", "source_bytes":1,
                 "source_sha256":"...", "translation_state":"...",
                 "translation_evidence":"authority/path#locator"}],
      "rights_components": [{"id":"primary", "status":"verified",
                              "license":"CC BY"}],
      "artifacts": [{"path":"...", "bytes":1, "sha256":"...",
                      "role":"reader", "media_type":"text/html"}],
      "reader_surfaces": [{"action":"html", "url":"https://...",
                            "state":"published", "primary":true,
                            "route":"/id/courses/A30/",
                            "public_readback":{"status":"pass", "http_status":200,
                              "bytes":1, "sha256":"...", "evidence_path":"..."}}]
    }

Optional ``relations``, ``build_recipes``, ``qa_events``, ``content_bindings``,
``capabilities``, and ``legacy_labels`` arrays/maps add evidence without
copying body text.  A missing capability is emitted explicitly as
``not_projected``; no translation state or learner route is inferred.

The output is a *candidate* package.  It records an explicit pending twin-build
QA event and must still be independently validated, admitted, and published by
the coordinator.  It never edits an owner tree or a central release.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import re
import shutil
import sys
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from v231_adapter_common import (
    CAPABILITY_NAMES,
    RECORD_TYPE_BY_TABLE,
    TABLE_ORDER,
    AdapterError,
    canonical_row_sha256,
    compact_json,
    file_fact,
    identity_set_sha256,
    inventory_sha256,
    make_row,
    package_payload_files,
    projection_id,
    read_json,
    require,
    safe_relative_path,
    sha256_bytes,
    sha256_file,
    sort_table_rows,
    tree_identity,
    write_checksums,
    write_csv_surfaces,
    write_json,
    write_tables,
)


ALLOWED_ROLES = {"A30", "B95", "C140"}
ALL_ROLES = [
    "A00", "A10", "A20", "A30", "B10", "B20", "B30", "B40", "B50", "B60",
    "B70", "B80", "B90", "B95", "C10", "C20", "C30", "C40", "C50", "C60",
    "C70", "C80", "C90", "C100", "C110", "C120", "C130", "C140", "D10",
    "D20", "D30", "D40", "D50", "D60", "D70", "D80", "D90", "D100", "D110",
    "D120",
]
SCHEMA_FILES = {
    "lane-adapter-v2.3.1.schema.json": "backend/v2.3/schema/lane-adapter-v2.3.1.schema.json",
    "capability-declarations-v0.2.schema.json": "backend/v2.3/schema/capability-declarations-v0.2.schema.json",
    "namespace-crosswalk-v0.2.schema.json": "backend/v2.3/schema/namespace-crosswalk-v0.2.schema.json",
    "translation-state-index-v0.2.schema.json": "backend/v2.3/schema/translation-state-index-v0.2.schema.json",
    "csv-projection-manifest-v0.2.schema.json": "backend/v2.3/schema/csv-projection-manifest-v0.2.schema.json",
    "scope-declaration-v0.2.schema.json": "backend/v2.3/schema/scope-declaration-v0.2.schema.json",
    "global-capability-contract-v0.1.0.json": "backend/v2.2/global-capability-contract-v0.1.0.json",
}
TOOLING_FILES = {
    "build_gap_adapters_v231.py": "backend/v2.3/scripts/build_gap_adapters_v231.py",
    "v231_adapter_common.py": "backend/v2.3/scripts/v231_adapter_common.py",
    "validate_lane_adapter_v231.py": "backend/v2.3/scripts/validate_lane_adapter_v231.py",
}
FORBIDDEN_PROSE_KEYS = {
    "body", "body_text", "textbook_prose", "source_prose", "target_prose",
    "source_text", "target_text", "solution_text", "proof_text", "exercise_text",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
URN_RE = re.compile(r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
URL_RE = re.compile(r"^https://[^\s]+$")


def reject_prose(value: Any, location: str = "$") -> None:
    """Reject body-bearing fields so a thin adapter cannot copy a book."""
    if isinstance(value, Mapping):
        for key, child in value.items():
            require(str(key) not in FORBIDDEN_PROSE_KEYS, f"prose-bearing field is forbidden: {location}.{key}")
            reject_prose(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_prose(child, f"{location}[{index}]")


def require_sha(value: Any, label: str) -> str:
    digest = str(value).lower()
    require(bool(SHA256_RE.fullmatch(digest)), f"{label} is not a lowercase SHA-256")
    return digest


def require_timestamp(value: Any) -> str:
    text = str(value)
    try:
        dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AdapterError(f"recorded_at is not ISO-8601: {text}") from exc
    return text


def normalized_fact(raw: Mapping[str, Any], *, default_base: str, label: str) -> dict[str, Any]:
    require(isinstance(raw, Mapping), f"{label} must be an object")
    path = str(raw.get("path", ""))
    require(path and not re.match(r"^[A-Za-z]:", path) and not path.startswith("//"), f"{label} path must be relative")
    path = safe_relative_path(path)
    base = str(raw.get("path_base", default_base))
    require(base in {"program_repository_root", "owner_package_root", "package_root"}, f"{label} path_base invalid")
    result: dict[str, Any] = {
        "path": path,
        "path_base": base,
        "role": str(raw.get("role", label)),
        "bytes": int(raw.get("bytes", -1)),
        "sha256": require_sha(raw.get("sha256", ""), f"{label}.sha256"),
    }
    require(result["bytes"] >= 0, f"{label}.bytes must be non-negative")
    for key in ("records", "record_id_set_sha256"):
        if key in raw:
            result[key] = int(raw[key]) if key == "records" else require_sha(raw[key], f"{label}.{key}")
    return result


def verify_external_fact(fact: Mapping[str, Any], repository_root: Path | None, owner_root: Path | None) -> str:
    base = str(fact.get("path_base", ""))
    if base == "package_root":
        return "package_root"
    root = repository_root if base == "program_repository_root" else owner_root if base == "owner_package_root" else None
    if root is None:
        return "not_replayed"
    path = root.joinpath(*PurePosixPath(str(fact["path"])).parts)
    require(path.is_file(), f"missing external authority: {fact['path']}")
    require(path.stat().st_size == fact["bytes"], f"external byte drift: {fact['path']}")
    require(sha256_file(path) == fact["sha256"], f"external hash drift: {fact['path']}")
    return "replayed"


def copy_exact(source: Path, target: Path) -> dict[str, Any]:
    require(source.is_file(), f"missing source file: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    require(target.read_bytes() == source.read_bytes(), f"copy mismatch: {source}")
    return file_fact(target, target.relative_to(target.parents[1]).as_posix(), "copied_source")


def local_package_fact(path: Path, package: Path, role: str, **extra: Any) -> dict[str, Any]:
    relative = path.relative_to(package).as_posix()
    return file_fact(path, relative, role, **extra)


def row(
    namespace: uuid.UUID,
    table: str,
    semantic_key: str,
    payload: Mapping[str, Any],
    *,
    dataset_id: str,
    owner_id: str,
    recorded_at: str,
    normalized_state: str = "candidate",
    owner_native_state: str | None = None,
) -> dict[str, Any]:
    return make_row(
        namespace,
        RECORD_TYPE_BY_TABLE[table],
        semantic_key,
        payload,
        dataset_id=dataset_id,
        owner_authority_id=owner_id,
        recorded_at=recorded_at,
        normalized_state=normalized_state,
        owner_native_state=owner_native_state,
    )


def source_fact_from_unit(unit: Mapping[str, Any], prefix: str = "source") -> dict[str, Any]:
    raw_path = str(unit[f"{prefix}_path"])
    require(raw_path and not re.match(r"^[A-Za-z]:", raw_path) and not raw_path.startswith("//"), f"unit {prefix}_path must be relative")
    return {
        "path": safe_relative_path(raw_path),
        "bytes": int(unit[f"{prefix}_bytes"]),
        "sha256": require_sha(unit[f"{prefix}_sha256"], f"unit.{prefix}_sha256"),
    }


def build_tables(spec: Mapping[str, Any], namespace: uuid.UUID, package_id: str, dataset_id: str,
                 edition_id: str, owner_id: str, recorded_at: str) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    role = str(spec["role_id"])
    tables = {name: [] for name in TABLE_ORDER}
    owner_payload = {
        "role_id": role,
        "title": str(spec["title"]),
        "owner_namespace": str(spec["owner_namespace"]),
        "authority_facts": copy.deepcopy(spec["authorities"]),
        "curriculum_authority": copy.deepcopy(spec["curriculum_authority"]),
        "public_authority_status": str(spec.get("public_authority_status", "unverified")),
    }
    tables["owner_authorities"].append(row(namespace, "owner_authorities", f"{role.lower()}:owner-authority", owner_payload, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))
    tables["datasets"].append(row(namespace, "datasets", str(spec["dataset_key"]), {
        "course_id": str(spec["course_id"]), "curriculum_role_id": role, "title": str(spec["title"]),
        "edition_id": edition_id, "owner_authority_id": owner_id,
    }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))
    tables["editions"].append(row(namespace, "editions", f"{role.lower()}:edition", {
        "dataset_id": dataset_id, "edition_label": str(spec.get("edition_label", "unversioned")),
        "authority_facts": copy.deepcopy(spec["authorities"]), "source_format": str(spec.get("source_format", "unknown")),
    }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))

    units = sorted(spec["units"], key=lambda item: int(item["ordinal"]))
    unit_ids: dict[str, str] = {}
    for item in units:
        native_id = str(item["native_id"])
        unit_key = f"{role.lower()}:unit:{native_id}"
        projected_id = projection_id(namespace, "unit", unit_key)
        unit_ids[native_id] = projected_id
        src = source_fact_from_unit(item)
        payload = {
            "course_id": str(spec["course_id"]), "edition_id": edition_id, "native_id": native_id,
            "ordinal": int(item["ordinal"]), "label": str(item.get("label", native_id)),
            "title": str(item["title"]), "owner_source_path": src["path"],
            "owner_source_bytes": src["bytes"], "owner_source_sha256": src["sha256"],
            "body_prose_copied": False, "learner_route_state": str(item.get("learner_route_state", "explicit_unavailable")),
            "unit_url": item.get("unit_url"),
        }
        if "target_path" in item:
            target = source_fact_from_unit(item, "target")
            payload.update({"owner_target_path": target["path"], "owner_target_bytes": target["bytes"], "owner_target_sha256": target["sha256"]})
        translation_state = item.get("translation_state")
        tables["units"].append(row(namespace, "units", unit_key, payload, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at, owner_native_state=str(translation_state) if translation_state is not None else None))
        tables["course_unit_memberships"].append(row(namespace, "course_unit_memberships", f"{role.lower()}:membership:{native_id}", {
            "course_id": str(spec["course_id"]), "edition_id": edition_id, "unit_id": projected_id, "native_id": native_id, "ordinal": int(item["ordinal"]),
        }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))
        tables["native_bindings"].append(row(namespace, "native_bindings", f"{role.lower()}:native-binding:{native_id}", {
            "source_namespace": str(spec["owner_namespace"]), "native_record_id": native_id,
            "projected_record_id": projected_id, "native_path": src["path"], "native_bytes": src["bytes"],
            "native_sha256": src["sha256"], "owner_id_preserved": True, "body_prose_copied": False,
        }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))
        if "target_path" in item:
            target = source_fact_from_unit(item, "target")
            tables["content_bindings"].append(row(namespace, "content_bindings", f"{role.lower()}:content-binding:{native_id}", {
                "unit_id": projected_id, "source_locale": str(item.get("source_locale", "en")), "target_locale": str(item.get("target_locale", "id-ID")),
                "source_path": src["path"], "source_bytes": src["bytes"], "source_sha256": src["sha256"],
                "target_path": target["path"], "target_bytes": target["bytes"], "target_sha256": target["sha256"],
                "translation_state": item.get("translation_state"), "translation_evidence": item.get("translation_evidence"),
            }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at, owner_native_state=str(item.get("translation_state")) if item.get("translation_state") is not None else None))
        tables["search_documents"].append(row(namespace, "search_documents", f"{role.lower()}:search:{native_id}", {
            "unit_id": projected_id, "ordinal": int(item["ordinal"]), "label": str(item.get("label", native_id)), "title": str(item["title"]),
        }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))

    for left, right in zip(units, units[1:]):
        tables["relations"].append(row(namespace, "relations", f"{role.lower()}:precedes:{left['native_id']}:{right['native_id']}", {
            "relation_type": "precedes_in_release_order", "source_unit_id": unit_ids[str(left["native_id"])], "target_unit_id": unit_ids[str(right["native_id"])],
        }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))
    for prerequisite in spec.get("prerequisite_course_ids", []):
        tables["relations"].append(row(namespace, "relations", f"{role.lower()}:course-prerequisite:{prerequisite}", {
            "relation_type": "course_prerequisite", "source_course_id": str(spec["course_id"]), "target_course_id": str(prerequisite),
        }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))
    for relation in spec.get("relations", []):
        relation = copy.deepcopy(dict(relation))
        relation_key = str(relation.pop("id", relation.get("relation_type", len(tables["relations"]))))
        require(str(relation.get("relation_type", "")), f"relation {relation_key} lacks relation_type")
        tables["relations"].append(row(namespace, "relations", f"{role.lower()}:relation:{relation_key}", relation, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))
    for binding in spec.get("content_bindings", []):
        binding = copy.deepcopy(dict(binding))
        binding_key = str(binding.pop("id", binding.get("native_id", len(tables["content_bindings"]))))
        require(str(binding.get("unit_id", "")) or str(binding.get("native_id", "")), f"content binding {binding_key} lacks unit identity")
        tables["content_bindings"].append(row(namespace, "content_bindings", f"{role.lower()}:extra-content-binding:{binding_key}", binding, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))

    for rights in spec["rights_components"]:
        rights_id = projection_id(namespace, "rights", f"{role.lower()}:rights:{rights['id']}")
        rights_payload = copy.deepcopy(dict(rights))
        tables["rights"].append(row(namespace, "rights", f"{role.lower()}:rights:{rights['id']}", rights_payload, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))
        tables["rights_assignments"].append(row(namespace, "rights_assignments", f"{role.lower()}:rights-assignment:{rights['id']}", {
            "rights_id": rights_id, "target_record_type": "dataset", "target_record_id": dataset_id, "component_id": str(rights["id"]),
        }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))

    artifact_ids: dict[str, str] = {}
    for artifact in spec.get("artifacts", []):
        key = str(artifact.get("id", artifact["path"]))
        artifact_path = str(artifact["path"])
        require(artifact_path and not re.match(r"^[A-Za-z]:", artifact_path) and not artifact_path.startswith("//"), f"artifact path must be relative: {key}")
        artifact_ids[key] = projection_id(namespace, "artifact", f"{role.lower()}:artifact:{key}")
        payload = copy.deepcopy(dict(artifact))
        payload["path"] = safe_relative_path(artifact_path)
        payload["bytes"] = int(payload["bytes"])
        payload["sha256"] = require_sha(payload["sha256"], f"artifact {key}")
        payload["body_prose_copied"] = False
        tables["artifacts"].append(row(namespace, "artifacts", f"{role.lower()}:artifact:{key}", payload, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))

    for recipe in spec.get("build_recipes", []):
        tables["build_recipes"].append(row(namespace, "build_recipes", f"{role.lower()}:build:{recipe.get('id', len(tables['build_recipes']))}", copy.deepcopy(dict(recipe)), dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))

    surface_ids: dict[str, str] = {}
    for surface in spec.get("reader_surfaces", []):
        key = str(surface.get("id", surface["action"]))
        url = str(surface["url"])
        require(URL_RE.fullmatch(url), f"reader surface URL must be HTTPS: {key}")
        state = str(surface.get("state", "unknown"))
        if state == "published":
            readback = surface.get("public_readback")
            require(isinstance(readback, Mapping) and readback.get("status") == "pass" and int(readback.get("http_status", 0)) == 200, f"published surface lacks passing readback: {key}")
            require_sha(readback.get("sha256"), f"reader surface readback {key}")
            evidence_path = str(readback.get("evidence_path", ""))
            require(evidence_path and not re.match(r"^[A-Za-z]:", evidence_path) and not evidence_path.startswith("//"), f"reader surface evidence path must be relative: {key}")
            safe_relative_path(evidence_path)
        surface_ids[key] = projection_id(namespace, "reader_surface", f"{role.lower()}:surface:{key}")
        payload = copy.deepcopy(dict(surface))
        payload["url"] = url
        payload["state"] = state
        payload["artifact_id"] = artifact_ids.get(str(surface.get("artifact_id")))
        payload["machine_data_is_learner_destination"] = False
        tables["reader_surfaces"].append(row(namespace, "reader_surfaces", f"{role.lower()}:surface:{key}", payload, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at, normalized_state=state))
        route = surface.get("route")
        if route:
            require(str(route).startswith("/"), f"route must be site-relative: {key}")
            tables["routes"].append(row(namespace, "routes", f"{role.lower()}:route:{key}", {
                "route": str(route), "reader_surface_id": surface_ids[key], "state": state, "action": str(surface["action"]),
            }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at, normalized_state=state))

    for event in spec.get("qa_events", []):
        tables["qa_events"].append(row(namespace, "qa_events", f"{role.lower()}:qa:{event.get('id', len(tables['qa_events']))}", copy.deepcopy(dict(event)), dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))
    tables["qa_events"].append(row(namespace, "qa_events", f"{role.lower()}:qa:adapter-candidate", {
        "event_type": "adapter_generation", "status": "pending_independent_twin_replay", "scope": "thin_zero_copy_envelope",
    }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))
    profile_id = projection_id(namespace, "adapter_profile", f"{role.lower()}:profile:v2.3.1")
    tables["adapter_profiles"].append(row(namespace, "adapter_profiles", f"{role.lower()}:profile:v2.3.1", {
        "contract": "2.3.1", "role_id": role, "owner_native_authoritative": True,
        "full_prose_centralized": False, "owner_ids_reminted": False, "machine_data_is_learner_destination": False,
    }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))
    tables["adapter_runs"].append(row(namespace, "adapter_runs", f"{role.lower()}:run:{recorded_at}", {
        "profile_id": profile_id, "scope": "candidate", "deterministic_replay_state": "pending_independent_twin_replay",
    }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))
    for native_id, projected_id in unit_ids.items():
        tables["identity_crosswalks"].append(row(namespace, "identity_crosswalks", f"{role.lower()}:crosswalk:{native_id}", {
            "source_namespace": str(spec["owner_namespace"]), "source_record_id": native_id, "source_record_type": "native_unit",
            "target_namespace": str(namespace), "target_record_id": projected_id, "target_record_type": "unit",
            "cardinality": "one_to_one", "mapping_state": "mapped", "reverse_recipe": "lookup payload.native_id",
        }, dataset_id=dataset_id, owner_id=owner_id, recorded_at=recorded_at))
    return tables, {"unit_ids": unit_ids, "artifact_ids": artifact_ids, "surface_ids": surface_ids, "profile_id": profile_id}


def capability_sidecar(spec: Mapping[str, Any], tables: Mapping[str, list[dict[str, Any]]], package: Path,
                       package_id: str, dataset_id: str, authority_facts: list[dict[str, Any]], schema_facts: Mapping[str, dict[str, Any]],
                       recorded_at: str) -> dict[str, Any]:
    unit_ids = [str(row["id"]) for row in tables["units"]]
    defaults = {
        "structure_localization": ("materialized", len(unit_ids), len(unit_ids), "projected_records", ["units and memberships preserve source topology"]),
        "terminology": ("not_projected", 0, 0, "none", ["no terminology shard supplied"]),
        "mathematical_preservation": ("referenced_native_shards", len(unit_ids), 0, "native_shard_records", ["source hashes remain owner-native"]),
        "assessment_support": ("not_projected", 0, 0, "none", ["no assessment shard supplied"]),
        "assets": (("referenced_native_shards", len(spec.get("artifacts", [])), 0, "native_shard_records", ["artifact closure remains external"]) if spec.get("artifacts") else ("not_projected", 0, 0, "none", ["no asset/artifact shard supplied"])),
        "accessibility": ("not_projected", 0, 0, "none", ["no accessibility shard supplied"]),
        "corrections": ("not_projected", 0, 0, "none", ["no correction shard supplied"]),
        "computational_interactives": ("not_projected", 0, 0, "none", ["no computational shard supplied"]),
        "publication": ("referenced_native_shards", len(authority_facts), 0, "native_shard_records", ["publication facts remain authority-bound"]),
        "research_support": ("not_projected", 0, 0, "none", ["no research-support shard supplied"]),
    }
    configured = spec.get("capabilities", {})
    declarations: list[dict[str, Any]] = []
    for name in CAPABILITY_NAMES:
        raw = dict(configured.get(name, {})) if isinstance(configured, Mapping) else {}
        state, native_count, projected_count, scope, rules = defaults[name]
        state = str(raw.get("state", state))
        native_count = int(raw.get("native_count", native_count))
        projected_count = int(raw.get("projected_count", projected_count))
        scope = str(raw.get("identity_set_scope", scope))
        rules = [str(item) for item in raw.get("closure_rules", rules)]
        require(state in {"materialized", "referenced_native_shards", "not_projected", "absent"}, f"invalid capability state: {name}")
        ids = unit_ids if scope == "projected_records" else []
        refs = [file_fact(package / "tables" / "units.jsonl", "tables/units.jsonl", "capability_shard", records=len(unit_ids), record_id_set_sha256=identity_set_sha256(unit_ids))] if state == "materialized" else authority_facts if state == "referenced_native_shards" else []
        digest = identity_set_sha256(ids) if ids else None
        declarations.append({
            "name": name, "version": "0.1.0", "state": state,
            "schema_binding": schema_facts["capability-declarations-v0.2.schema.json"], "shard_refs": refs,
            "native_count": native_count, "projected_count": projected_count,
            "identity_set_sha256": digest, "identity_set_scope": scope,
            "closure_rules": rules,
            "loss_gap_report": {"status": "closed" if state in {"materialized", "referenced_native_shards"} else "declared_limitation", "reason": str(raw.get("loss_gap_reason", "candidate lane does not project this capability"))},
        })
    return {
        "$schema": "schema/capability-declarations-v0.2.schema.json",
        "schema_id": "interlanguage/global-modular-mathematics-capability-declarations/0.2.0",
        "schema_version": "0.2.0", "package_id": package_id, "dataset_id": dataset_id,
        "contract_binding": schema_facts["global-capability-contract-v0.1.0.json"], "capabilities": declarations,
        "legacy_labels": copy.deepcopy(spec.get("legacy_labels", [])),
        "namespace_crosswalk_binding": {"path": "namespace-crosswalk-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "csv_projection_binding": {"path": "csv-projection-manifest-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "translation_state_binding": {"path": "translation-state-index-v0.2.0.json", "binding_state": "sealed_by_package_manifest"},
        "rights_cross_cutting": {"state": "referenced_native_shards", "shard_refs": [file_fact(package / "tables" / "rights.jsonl", "tables/rights.jsonl", "rights_shard", records=len(tables["rights"]))], "native_count": len(tables["rights"]), "identity_set_sha256": identity_set_sha256(str(row["id"]) for row in tables["rights"]), "closure_rules": ["component rights remain separate"]},
        "recorded_at": recorded_at,
    }


def build_package(spec_path: Path, output: Path, repository_root: Path | None, owner_root: Path | None, replace: bool) -> dict[str, Any]:
    raw = json.loads(spec_path.read_text(encoding="utf-8"))
    reject_prose(raw)
    require(str(raw.get("role_id")) in ALLOWED_ROLES, f"role must be one of {sorted(ALLOWED_ROLES)}")
    role = str(raw["role_id"])
    require(str(raw.get("course_id", "")), "course_id is required")
    require(str(raw.get("dataset_key", "")), "dataset_key is required")
    require(str(raw.get("owner_namespace", "")), "owner_namespace is required")
    recorded_at = require_timestamp(raw.get("recorded_at"))
    namespace = uuid.UUID(str(raw.get("namespace", "")))
    authorities = [normalized_fact(item, default_base="owner_package_root", label=f"authority[{i}]") for i, item in enumerate(raw.get("authorities", []))]
    require(authorities, "at least one owner authority is required")
    curriculum_authority = normalized_fact(raw.get("curriculum_authority", {}), default_base="program_repository_root", label="curriculum_authority")
    require(all(fact["path_base"] != "package_root" for fact in authorities + [curriculum_authority]), "external authorities may not use package_root")
    authorities.append(curriculum_authority)
    # Downstream tables must carry the normalized, relative authority facts,
    # never an untrusted copy of the input object.
    raw["authorities"] = copy.deepcopy(authorities[:-1])
    raw["curriculum_authority"] = copy.deepcopy(curriculum_authority)
    for fact in authorities:
        verify_external_fact(fact, repository_root, owner_root)
    units = raw.get("units")
    require(isinstance(units, list) and units, "units must be a non-empty array")
    ordinals = [int(item.get("ordinal", -1)) for item in units]
    native_ids = [str(item.get("native_id", "")) for item in units]
    require(all(item > 0 for item in ordinals) and len(ordinals) == len(set(ordinals)), "unit ordinals must be positive and unique")
    require(all(native_ids) and len(native_ids) == len(set(native_ids)), "native unit IDs must be unique")
    for item in units:
        for key in ("native_id", "ordinal", "title", "source_path", "source_bytes", "source_sha256"):
            require(key in item, f"unit field missing: {key}")
        require_sha(item["source_sha256"], f"unit {item['native_id']} source_sha256")
        if "target_sha256" in item:
            for key in ("target_path", "target_bytes"):
                require(key in item, f"target field missing for unit {item['native_id']}: {key}")
            require_sha(item["target_sha256"], f"unit {item['native_id']} target_sha256")
            raw_target_path = str(item["target_path"])
            require(raw_target_path and not re.match(r"^[A-Za-z]:", raw_target_path) and not raw_target_path.startswith("//"), f"unit {item['native_id']} target_path must be relative")
        raw_source_path = str(item["source_path"])
        require(raw_source_path and not re.match(r"^[A-Za-z]:", raw_source_path) and not raw_source_path.startswith("//"), f"unit {item['native_id']} source_path must be relative")
        if item.get("unit_url") is not None:
            require(URL_RE.fullmatch(str(item["unit_url"])), f"unit {item['native_id']} unit_url must be HTTPS")
        if item.get("translation_state") is not None:
            require(item.get("translation_evidence"), f"translation state lacks evidence: {item['native_id']}")
    rights = raw.get("rights_components")
    require(isinstance(rights, list) and rights, "rights_components must be non-empty")
    for item in rights:
        require(str(item.get("id", "")) and str(item.get("status", "")), "each rights component needs id and status")
    package_id = projection_id(namespace, "lane_adapter_package", f"{role.lower()}:{raw['dataset_key']}:2.3.1")
    dataset_id = projection_id(namespace, "dataset", str(raw["dataset_key"]))
    edition_id = projection_id(namespace, "edition", f"{role.lower()}:edition")
    owner_id = projection_id(namespace, "owner_authority", f"{role.lower()}:owner-authority")
    extension_id = projection_id(namespace, "lane_adapter_extension", f"{role.lower()}:2.3.1")
    if output.exists():
        require(replace, "output exists; pass --replace")
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    # ``repository_root`` is the authority-replay root and may be a temporary
    # mirror or an owner-specific checkout.  Schemas/tooling must always come
    # from this coordinator checkout, otherwise a caller could accidentally
    # package a foreign or incomplete contract tree.
    repo_root = Path(__file__).resolve().parents[3]
    for name, relative in SCHEMA_FILES.items():
        source = repo_root / relative
        require(source.is_file(), f"missing schema source: {source}")
        target = output / "schema" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for name, relative in TOOLING_FILES.items():
        source = repo_root / relative
        require(source.is_file(), f"missing tooling source: {source}")
        target = output / "tooling" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    tables, metadata = build_tables(raw, namespace, package_id, dataset_id, edition_id, owner_id, recorded_at)
    sort_table_rows(tables)
    write_tables(output, tables)
    schema_facts = {name: local_package_fact(output / "schema" / name, output, "schema") for name in SCHEMA_FILES}
    csv_manifest = write_csv_surfaces(output, tables, package_id, recorded_at)
    write_json(output / "csv-projection-manifest-v0.2.0.json", csv_manifest)
    unit_ids = metadata["unit_ids"]
    mappings = [{
        "source_namespace": str(raw["owner_namespace"]), "target_namespace": str(namespace), "source_record_id": native_id,
        "target_record_id": projected_id, "source_record_type": "native_unit", "target_record_type": "unit",
        "cardinality": "one_to_one", "mapping_state": "mapped", "reverse_recipe": "lookup payload.native_id",
        "evidence_refs": [str(fact["path"]) for fact in authorities], "identity_set_sha256": identity_set_sha256(unit_ids.values()),
    } for native_id, projected_id in sorted(unit_ids.items())]
    write_json(output / "namespace-crosswalk-v0.2.0.json", {
        "$schema": "schema/namespace-crosswalk-v0.2.schema.json", "schema_id": "interlanguage/global-modular-mathematics-namespace-crosswalk/0.2.0", "schema_version": "0.2.0", "package_id": package_id,
        "profiles": [{"namespace": str(raw["owner_namespace"]), "role": "owner_native"}, {"namespace": str(namespace), "role": "adapter_projection"}, {"namespace": "7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd", "role": "global_exchange"}],
        "mappings": mappings, "unmaterialized_candidates": [], "identity_sets": {"source_unit_ids": identity_set_sha256(unit_ids.keys()), "target_unit_ids": identity_set_sha256(unit_ids.values())}, "recorded_at": recorded_at,
    })
    translation_records = []
    for item in sorted(units, key=lambda entry: int(entry["ordinal"])):
        if item.get("translation_state") is None:
            continue
        translation_records.append({"projected_unit_id": unit_ids[str(item["native_id"])], "native_unit_id": str(item["native_id"]), "state": str(item["translation_state"]), "evidence_refs": [str(item["translation_evidence"])], "source_sha256": require_sha(item["source_sha256"], "translation source")})
    write_json(output / "translation-state-index-v0.2.0.json", {
        "$schema": "schema/translation-state-index-v0.2.schema.json", "schema_id": "interlanguage/global-modular-mathematics-translation-state-index/0.2.0", "schema_version": "0.2.0", "package_id": package_id, "dataset_id": dataset_id,
        "authority_bindings": authorities, "coverage": {"course_id": str(raw["course_id"]), "granularity": "unit", "authority_rows": len(translation_records), "indexed_rows": len(translation_records), "inferred_rows": 0}, "states": sorted({str(item["state"]) for item in translation_records}) or ["not_indexed"], "records": translation_records, "identity_set_sha256": identity_set_sha256(str(item["projected_unit_id"]) for item in translation_records), "no_inference": True, "recorded_at": recorded_at,
    })
    write_json(output / "scope-declaration-v0.2.0.json", {
        "$schema": "schema/scope-declaration-v0.2.schema.json", "schema_id": "interlanguage/global-modular-mathematics-backend-scope/0.2.0", "schema_version": "0.2.0", "package_id": package_id, "dataset_id": dataset_id, "scope_kind": "lane_adapter", "course_ids": [str(raw["course_id"])], "curriculum_role_ids": [role], "aggregate_conformance_claim": False, "unbound_curriculum_role_ids": [item for item in ALL_ROLES if item != role], "owner_authority_binding": authorities[0], "curriculum_authority_binding": curriculum_authority, "limitations": ["candidate package; independent twin replay and owner admission remain pending", "full prose remains owner-native", "unsupported capabilities are not projected"], "recorded_at": recorded_at,
    })
    capability = capability_sidecar(raw, tables, output, package_id, dataset_id, authorities, schema_facts, recorded_at)
    write_json(output / "capability-declarations-v0.2.0.json", capability)
    sidecar_names = ["capability-declarations-v0.2.0.json", "namespace-crosswalk-v0.2.0.json", "translation-state-index-v0.2.0.json", "csv-projection-manifest-v0.2.0.json", "scope-declaration-v0.2.0.json"]
    sidecars = [local_package_fact(output / name, output, "sidecar") for name in sidecar_names]
    payload_facts = package_payload_files(output)
    builder_fact = local_package_fact(output / "tooling" / "build_gap_adapters_v231.py", output, "builder")
    validator_fact = local_package_fact(output / "tooling" / "validate_lane_adapter_v231.py", output, "validator")
    manifest = {
        "$schema": "schema/lane-adapter-v2.3.1.schema.json", "schema_id": "interlanguage/global-modular-mathematics-lane-adapter/2.3.1", "schema_version": "2.3.1", "package_id": package_id, "dataset_id": dataset_id, "extension_id": extension_id, "extension_version": "0.1.0", "recorded_at": recorded_at,
        "scope_declaration": local_package_fact(output / "scope-declaration-v0.2.0.json", output, "scope"), "authorities": authorities, "sidecars": sidecars,
        "csv_projection": {"manifest": local_package_fact(output / "csv-projection-manifest-v0.2.0.json", output, "csv_manifest"), "table_csv_count": len(TABLE_ORDER), "aggregate_csv_count": 1, "record_count": sum(len(rows) for rows in tables.values()), "roundtrip_state": "pass"},
        "build": {"builder": builder_fact, "validator": validator_fact, "canonical_serialization": {"scope": "builder_generated_json_jsonl_and_csv_only", "encoding": "UTF-8", "newline": "LF", "json_keys": "lexicographically_sorted", "trailing_newline": True, "copied_schema_and_tool_files": "preserved_exact_source_bytes"}, "deterministic_replay": "byte_identical", "build_a_sha256": inventory_sha256(payload_facts), "build_b_sha256": inventory_sha256(payload_facts)},
        "files": payload_facts,
        "seal_policy": {"algorithm": "sha256-sorted-path-bytes-v1", "seal_file": "seal.json", "seal_excluded_from_own_digest": True, "binds": ["manifest.json", "all payload files", "PACKAGE_CHECKSUMS.sha256"]},
        "zero_copy_policy": {"owner_native_authoritative": True, "full_prose_centralized": False, "owner_ids_reminted": False, "aggregate_conformance_claim": False, "machine_data_is_learner_destination": False, "machine_surfaces_secondary": True},
    }
    write_json(output / "manifest.json", manifest)
    manifest_fact = local_package_fact(output / "manifest.json", output, "manifest")
    seal_facts = sorted(payload_facts + [manifest_fact], key=lambda fact: str(fact["path"]))
    write_json(output / "seal.json", {"schema_id": "program-matematika-indonesia/lane-adapter-seal/1", "algorithm": "sha256-sorted-path-bytes-v1", "package_id": package_id, "seal_excluded_from_own_digest": True, "files": seal_facts, "file_count": len(seal_facts), "bytes": sum(int(fact["bytes"]) for fact in seal_facts), "aggregate_sha256": inventory_sha256(seal_facts)})
    write_checksums(output, package_payload_files(output) + [manifest_fact])
    return {"status": "candidate_built", "role_id": role, "package": str(output), "package_id": package_id, "dataset_id": dataset_id, "payload_files": len(payload_facts), "payload_bytes": sum(int(fact["bytes"]) for fact in payload_facts), "unit_count": len(units), "note": "Run validate_lane_adapter_v231.py with independent A/B trees before admission."}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True, help="evidence-first gap lane specification JSON")
    parser.add_argument("--output", type=Path, required=True, help="new candidate package directory")
    parser.add_argument("--repository-root", type=Path, help="central repository root for authority replay")
    parser.add_argument("--owner-package-root", type=Path, help="owner package root for authority replay")
    parser.add_argument("--replace", action="store_true", help="replace only the explicit output directory")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = build_package(args.spec.resolve(), args.output.resolve(), args.repository_root.resolve() if args.repository_root else None, args.owner_package_root.resolve() if args.owner_package_root else None, args.replace)
        print(compact_json(result))
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
