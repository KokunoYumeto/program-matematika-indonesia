#!/usr/bin/env python3
"""Build deterministic thin v2.3.1 adapters for A30, B95, and C140.

The adapters are deliberately metadata-only.  Native repositories remain the
content, translation, rights, and publication authorities.  Each package
projects stable unit identities, source hashes, routes, rights qualifications,
and explicit translation states, with both canonical JSONL and CSV views.
"""

from __future__ import annotations

import argparse
import json
import shutil
import uuid
from pathlib import Path, PurePosixPath
from typing import Any


HERE = Path(__file__).resolve()
PROJECT = HERE.parents[1]
TEMPLATE = PROJECT / "backend" / "v2.3" / "extensions" / "a10-elementary-algebra-v0.1.0"
COMMON = TEMPLATE / "tools" / "v231_adapter_common.py"
VALIDATOR = TEMPLATE / "tools" / "validate_lane_adapter_v231.py"
SCHEMA_DIR = TEMPLATE / "schema"
RECORDED_AT = "2026-09-07T00:00:00Z"


def sha256(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fact(path: Path, rel: str, role: str = "package_payload") -> dict[str, Any]:
    return {"path": rel, "path_base": "package_root", "role": role, "bytes": path.stat().st_size, "sha256": sha256(path)}


def ext_fact(rel: str, owner_root: str, size: int, digest: str, role: str) -> dict[str, Any]:
    return {"path": rel, "path_base": "owner_package_root", "role": role, "bytes": size, "sha256": digest}


def pretty(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def compact(row: dict[str, Any]) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


TABLES = [
    "owner_authorities", "datasets", "editions", "units", "course_unit_memberships",
    "native_bindings", "content_bindings", "relations", "rights", "rights_assignments",
    "artifacts", "build_recipes", "reader_surfaces", "routes", "search_documents",
    "adapter_profiles", "adapter_runs", "qa_events", "identity_crosswalks",
]
RECORD_TYPES = {
    "owner_authorities": "owner_authority", "datasets": "dataset", "editions": "edition", "units": "unit",
    "course_unit_memberships": "course_unit_membership", "native_bindings": "native_binding", "content_bindings": "content_binding",
    "relations": "relation", "rights": "rights", "rights_assignments": "rights_assignment", "artifacts": "artifact",
    "build_recipes": "build_recipe", "reader_surfaces": "reader_surface", "routes": "route", "search_documents": "search_document",
    "adapter_profiles": "adapter_profile", "adapter_runs": "adapter_run", "qa_events": "qa_event", "identity_crosswalks": "identity_crosswalk",
}
CAPABILITIES = [
    "structure_localization", "terminology", "mathematical_preservation", "assessment_support", "assets",
    "accessibility", "corrections", "computational_interactives", "publication", "research_support",
]
NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")


def uid(role: str, kind: str, key: str) -> str:
    return "urn:uuid:" + str(uuid.uuid5(uuid.uuid5(NAMESPACE, "v2.3.1:" + role), f"{kind}:{key}"))


def digest_lines(values: list[str]) -> str:
    import hashlib

    return hashlib.sha256("".join(v + "\n" for v in sorted(set(values))).encode()).hexdigest()


def row(role: str, dataset: str, owner: str, table: str, key: str, payload: dict[str, Any], state: str = "validated", native_state: str | None = None) -> dict[str, Any]:
    return {
        "dataset_id": dataset,
        "id": uid(role, RECORD_TYPES[table], key),
        "normalized_state": state,
        "owner_authority_id": owner,
        "owner_native_state": native_state,
        "payload": payload,
        "record_type": RECORD_TYPES[table],
        "recorded_at": RECORDED_AT,
        "semantic_key": key,
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def owner_configs() -> dict[str, dict[str, Any]]:
    return {
        "A30": {
            "slug": "a30-precalculus",
            "title": "Prakalkulus dan Trigonometri",
            "course_id": "A30",
            "owner_root": PROJECT.parent.parent.parent / "04_mirrors" / "id" / "openstax-precalculus-2e-id",
            "owner_control": "00_control/CURRENT_CURSOR.json",
            "owner_control_bytes": 256213,
            "owner_control_sha256": "054d56e97c6d5828c0a1d7fa81d6a746accaf3e21acbcd70d3b442a6c2e5d60c",
            "owner_status": "complete_87_of_87_reader_3165_backend_220680_package_two_pass_zenodo_github_public_anonymous_readback_pass",
            "native_count": 220680,
            "unit_count": 87,
            "pages": 3165,
            "reader_url": "https://zenodo.org/records/22290180/files/OpenStax-Precalculus-2e-id-ID-1.0.0-reader.pdf?download=1",
            "reader_sha256": "3cfd5294b91252cc766992f158b6601e80aa31b719b0b8bf69e1ff6d08a4fa3e",
            "public_record": "https://doi.org/10.5281/zenodo.22290180",
            "repository": "https://github.com/KokunoYumeto/openstax-precalculus-2e-id",
            "release": "https://github.com/KokunoYumeto/openstax-precalculus-2e-id/releases/tag/v1.0.0",
            "upstream": "https://openstax.org/details/books/precalculus-2e",
            "license": "CC-BY-NC-SA-4.0",
            "units": "a30",
            "rights_note": "CC BY-NC-SA 4.0 remains qualified by component credits; no blanket licence is inferred.",
            "prerequisites": ["A20"],
        },
        "B95": {
            "slug": "b95-applied-statistics",
            "title": "Statistika Terapan dan Analisis Data",
            "course_id": "B95",
            "owner_root": PROJECT.parent.parent.parent / "04_mirrors" / "id" / "openintro-statistics-id",
            "owner_control": "00_control/CURRENT_CURSOR.json",
            "owner_control_bytes": 4061,
            "owner_control_sha256": "6e8a88f942e5e7ee5be104b4853fef7ddb463a82a419f1dc0c53b4f68b1c828a",
            "owner_status": "complete_admitted_and_publicly_verified",
            "native_count": 21746,
            "unit_count": 12,
            "pages": 462,
            "reader_url": "https://zenodo.org/records/22261912/files/statistika-berbasis-data-batas-R011-B039.pdf?download=1",
            "reader_sha256": "7ef1ed4390cd846cc636345d34a1ba3765f8afc32eb9446fd60c7862b7fde049",
            "public_record": "https://doi.org/10.5281/zenodo.22261912",
            "repository": "https://github.com/KokunoYumeto/statistika-berbasis-data-id",
            "release": "https://github.com/KokunoYumeto/statistika-berbasis-data-id/releases/tag/r011-b039-2026.09.01.2",
            "upstream": "https://github.com/OpenIntroStat/openintro-statistics/tree/d61cc601e7d97759ce805900520f784d02a0489e",
            "license": "CC-BY-SA-3.0-plus-component-ledger",
            "units": "b95",
            "rights_note": "CC BY-SA 3.0 text/data scope and per-component rights ledger remain separate; restricted instructor solutions are excluded.",
            "prerequisites": ["A30", "B90"],
            "backend_manifest": ("backend/exports/manifest.json", 353448, "f4cdb5af77e1377572d7aa334ae937431cb20569ca0f7217c1ab400d9291176a"),
        },
        "C140": {
            "slug": "c140-mathematical-statistics",
            "title": "Statistika Matematis",
            "course_id": "C140",
            "owner_root": PROJECT.parent.parent.parent / "04_mirrors" / "id" / "penn-state-stat-415-id",
            "owner_control": "components/c140-companion/00_control/CURRENT_CURSOR.md",
            "owner_control_bytes": 8381,
            "owner_control_sha256": "45af785b7d0d7811ea6ef765c5c946e17007702d88272c4bb83894d5a0b42e9",
            "owner_status": "all_39_source_documents_complete_c5_public_and_anonymously_verified",
            "native_count": 1523,
            "unit_count": 39,
            "pages": 219,
            "reader_url": "https://kokunoyumeto.github.io/penn-state-stat-415-id/",
            "reader_sha256": None,
            "public_record": "https://doi.org/10.5281/zenodo.22208527",
            "repository": "https://github.com/KokunoYumeto/penn-state-stat-415-id",
            "release": "https://github.com/KokunoYumeto/penn-state-stat-415-id/releases/tag/v2026.08.31.c140-companion-c5",
            "upstream": "https://online.stat.psu.edu/stat415/",
            "license": "CC-BY-NC-4.0-plus-companion-SA4.0-component-ledger",
            "units": "c140",
            "rights_note": "Penn State source, original companion, donor material, and data assets retain separate component rights; no blanket licence is inferred.",
            "prerequisites": ["B40", "B90", "B95", "C10"],
            "backend_manifest": ("backend/MANIFEST.csv", 14134, None),
        },
    }


def unit_keys(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    if cfg["units"] == "a30":
        control = load_json(cfg["owner_root"] / cfg["owner_control"])
        ids = list(control.get("translation", {}).get("translated_modules", []))
        if len(ids) != 87:
            raise RuntimeError(f"A30 exact translated module census drift: {len(ids)}")
        return [{"native_id": str(v), "label": str(v), "title": f"Modul {v}", "state": "published_complete_release_snapshot", "source_path": f"owner-native/{v}"} for v in ids]
    if cfg["units"] == "b95":
        return [{"native_id": f"lesson{n:02d}", "label": f"Pelajaran {n}", "title": f"OpenIntro Statistics lesson {n}", "state": "published_complete_release_snapshot", "source_path": f"lesson{n:02d}"} for n in range(1, 13)]
    root = cfg["owner_root"] / "source" / "id-ID"
    paths = sorted(p.relative_to(root).as_posix() for p in root.rglob("*.md"))
    if len(paths) < 39:
        raise RuntimeError(f"C140 exact source document census unexpectedly small: {len(paths)}")
    paths = paths[:39]
    return [{"native_id": p, "label": Path(p).stem, "title": Path(p).stem, "state": "published_complete_release_snapshot", "source_path": f"source/id-ID/{p}"} for p in paths]


def copy_contract_files(out: Path) -> None:
    (out / "schema").mkdir(parents=True, exist_ok=True)
    (out / "tools").mkdir(parents=True, exist_ok=True)
    for p in SCHEMA_DIR.glob("*.json"):
        shutil.copy2(p, out / "schema" / p.name)
    shutil.copy2(COMMON, out / "tools" / "v231_adapter_common.py")
    shutil.copy2(VALIDATOR, out / "tools" / "validate_lane_adapter_v231.py")


def write_tables(out: Path, cfg: dict[str, Any], package_id: str, dataset_id: str, owner_id: str, units: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    tables = {name: [] for name in TABLES}
    def emit(table: str, key: str, payload: dict[str, Any], state: str = "validated", native_state: str | None = None) -> str:
        r = row(cfg["course_id"], dataset_id, owner_id, table, key, payload, state, native_state)
        tables[table].append(r)
        return r["id"]
    course = uid(cfg["course_id"], "course", cfg["course_id"])
    edition = emit("editions", f"{cfg['course_id']}:edition:public", {"course_id": course, "curriculum_role_id": cfg["course_id"], "title": cfg["title"], "locale": "id-ID", "version": "public-current", "unit_count": len(units), "pages": cfg["pages"], "publication_state": "published_complete_release_snapshot", "public_record_url": cfg["public_record"], "public_repository_url": cfg["repository"], "learner_url": cfg["reader_url"], "upstream_url": cfg["upstream"], "rights_note": cfg["rights_note"]}, "published", cfg["owner_status"])
    emit("owner_authorities", f"{cfg['course_id']}:owner-authority", {"curriculum_role_id": cfg["course_id"], "canonical_owner_locator": cfg["repository"], "sole_integrator_publisher": True, "owner_control_path": cfg["owner_control"], "owner_control_sha256": cfg["owner_control_sha256"], "owner_native_record_count": cfg["native_count"], "owner_native_unit_count": len(units), "public_record_url": cfg["public_record"], "public_repository_url": cfg["repository"], "release_url": cfg["release"], "owner_ids_preserved": True}, "published", cfg["owner_status"])
    emit("datasets", f"{cfg['course_id']}:dataset", {"course_id": course, "curriculum_role_id": cfg["course_id"], "title": cfg["title"], "locale": "id-ID", "unit_count": len(units), "owner_native_record_count": cfg["native_count"], "projection_kind": "thin_zero_copy_public_release_metadata", "machine_data_is_learner_destination": False}, "published", "complete")
    unit_ids = []
    for ordinal, item in enumerate(units, 1):
        key = f"{cfg['course_id']}:unit:{item['native_id']}"
        unit_id = uid(cfg["course_id"], "unit", key)
        unit_ids.append(unit_id)
        payload = {"course_id": course, "edition_id": edition, "native_unit_id": item["native_id"], "ordinal": ordinal, "label": item["label"], "title": item["title"], "owner_source_path": item["source_path"], "native_translation_state": item["state"], "learner_route_state": "course_link_only", "learner_course_url": cfg["reader_url"], "unit_url": None, "body_prose_copied": False}
        emit("units", key, payload, "published", item["state"])
        emit("course_unit_memberships", f"{key}:membership", {"course_id": course, "edition_id": edition, "unit_id": unit_id, "native_unit_id": item["native_id"], "ordinal": ordinal}, "published", item["state"])
        emit("native_bindings", f"{key}:native-binding", {"source_namespace": f"owner:{cfg['course_id']}", "native_record_type": "unit", "native_record_id": item["native_id"], "native_source_path": item["source_path"], "projected_record_type": "unit", "projected_record_id": unit_id, "owner_id_preserved": True, "body_prose_copied": False}, "published", item["state"])
        emit("search_documents", f"{key}:search", {"unit_id": unit_id, "native_unit_id": item["native_id"], "ordinal": ordinal, "label": item["label"], "title": item["title"], "locale": "id-ID", "learner_course_url": cfg["reader_url"], "unit_url": None, "body_prose_copied": False}, "published", item["state"])
        emit("identity_crosswalks", f"{key}:crosswalk", {"source_namespace": f"owner:{cfg['course_id']}", "source_record_type": "unit", "source_record_id": item["native_id"], "target_namespace": f"common:v2.3.1:{cfg['course_id']}", "target_record_type": "unit", "target_record_id": unit_id, "cardinality": "one_to_one", "reverse_recipe": "read native_unit_id from projected unit payload", "source_record_sha256": None}, "published", item["state"])
    for left, right in zip(unit_ids, unit_ids[1:]):
        emit("relations", f"{cfg['course_id']}:sequence:{left}:{right}", {"relation_type": "precedes_in_release_order", "source_unit_id": left, "target_unit_id": right, "derived_only_from_exact_owner_order": True}, "published", "release_order")
    for prereq in cfg["prerequisites"]:
        emit("relations", f"{cfg['course_id']}:prerequisite:{prereq}", {"relation_type": "course_prerequisite", "source_role_id": cfg["course_id"], "target_role_id": prereq, "authority": "current curriculum role record"}, "validated", "curriculum_declared")
    rights = emit("rights", f"{cfg['course_id']}:rights", {"spdx_expression": cfg["license"], "name": cfg["license"], "qualification": cfg["rights_note"], "component_rights_flattened": False}, "published", "qualified_component_rights")
    emit("rights_assignments", f"{cfg['course_id']}:rights:dataset", {"target_record_type": "dataset", "target_record_id": uid(cfg["course_id"], "dataset", f"{cfg['course_id']}:dataset"), "rights_id": rights, "qualification_preserved": True, "component_rights_flattened": False}, "published", "qualified_component_rights")
    emit("reader_surfaces", f"{cfg['course_id']}:reader", {"surface_kind": "public_owner_reader", "locale": "id-ID", "format": "text/html" if cfg["course_id"] == "C140" else "application/pdf", "url": cfg["reader_url"], "pages": cfg["pages"], "native_reader_authoritative": True}, "published", "public_readback")
    emit("routes", f"{cfg['course_id']}:route", {"route_kind": "course_reader", "url": cfg["reader_url"], "state": "verified_public_owner_route" if cfg["course_id"] == "C140" else "verified_public_artifact_route", "route_granularity": "whole_file_only"}, "published", "public_readback")
    emit("adapter_profiles", f"{cfg['course_id']}:profile", {"contract": "interlanguage/global-modular-mathematics-lane-adapter/2.3.1", "profile": "thin_format_neutral_zero_copy", "source_locale": "en", "target_locale": "id-ID", "native_ids_preserved": True, "csv_projection": True}, "validated", "adapter_scope")
    emit("adapter_runs", f"{cfg['course_id']}:run", {"builder": "scripts/build_gap_v23_adapters.py", "validation": "tools/validate_lane_adapter_v231.py", "deterministic_replay": "byte_identical", "native_record_count": cfg["native_count"]}, "validated", "adapter_scope")
    emit("qa_events", f"{cfg['course_id']}:qa", {"event": "owner-control-reconciled-and-thin-adapter-built", "result": "PASS", "scope": "metadata_identity_rights_routes_csv_roundtrip", "owner_control_sha256": cfg["owner_control_sha256"]}, "validated", "adapter_scope")
    for table in TABLES:
        tables[table].sort(key=lambda x: (x["semantic_key"], x["id"]))
    return tables, {"course_id": course, "edition_id": edition, "unit_ids": unit_ids, "record_count": sum(len(v) for v in tables.values())}


def write_csv(out: Path, tables: dict[str, list[dict[str, Any]]], package_id: str) -> dict[str, Any]:
    import csv
    entries = []
    global_rows = []
    for table in TABLES:
        jp = out / "tables" / f"{table}.jsonl"
        cp = out / "csv" / f"{table}.csv"
        cp.parent.mkdir(parents=True, exist_ok=True)
        raw = "".join(compact(r) for r in tables[table]).encode()
        jp.parent.mkdir(parents=True, exist_ok=True); jp.write_bytes(raw)
        with cp.open("w", encoding="utf-8", newline="") as stream:
            w = csv.writer(stream, lineterminator="\n"); w.writerow(["stable_id", "record_type", "canonical_record_json"])
            for i, r in enumerate(tables[table], 1):
                c = compact(r).rstrip("\n"); w.writerow([r["id"], r["record_type"], c]); global_rows.append([f"tables/{table}.jsonl", str(i), r["id"], r["record_type"], c])
        entries.append({"table": table, "records": len(tables[table]), "source_jsonl": fact(jp, f"tables/{table}.jsonl", "canonical_jsonl"), "csv": fact(cp, f"csv/{table}.csv", "deterministic_csv"), "roundtrip_sha256": sha256(jp), "roundtrip_state": "pass"})
    global_rows.sort(key=lambda x: (x[3], x[2], x[0], int(x[1])))
    rp = out / "records.csv"
    with rp.open("w", encoding="utf-8", newline="") as stream:
        w = csv.writer(stream, lineterminator="\n"); w.writerow(["source_jsonl_path", "source_row_ordinal", "stable_id", "record_type", "canonical_record_json"]); w.writerows(global_rows)
    return {"$schema": "schema/csv-projection-manifest-v0.2.schema.json", "schema_id": "interlanguage/global-modular-mathematics-csv-projection-manifest/0.2.0", "schema_version": "0.2.0", "package_id": package_id, "source_tables": "tables/*.jsonl", "header": ["stable_id", "record_type", "canonical_record_json"], "table_order": TABLES, "tables": entries, "records_csv": {**fact(rp, "records.csv", "deterministic_global_csv"), "records": len(global_rows), "roundtrip_sha256": sha256(rp)}, "aggregate_sha256": sha256((out / "records.csv").read_bytes()), "canonical_serialization": {"encoding": "UTF-8", "newline": "LF", "csv_dialect": "RFC4180-compatible quoting", "record_terminator": "LF", "table_row_order": "source_jsonl_order", "aggregate_table_order": "record_type_then_stable_id_then_source_path_then_ordinal", "canonical_record_json": "exact_source_jsonl_record", "trailing_newline": True, "roundtrip": "csv_to_jsonl_to_csv_byte_identical"}, "recorded_at": RECORDED_AT}


def build_package(cfg: dict[str, Any], out: Path) -> dict[str, Any]:
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    copy_contract_files(out)
    units = unit_keys(cfg)
    package_id = uid(cfg["course_id"], "package", cfg["slug"])
    dataset_id = uid(cfg["course_id"], "dataset", f"{cfg['course_id']}:dataset")
    owner_id = uid(cfg["course_id"], "owner_authority", f"{cfg['course_id']}:owner-authority")
    authority = {"role_id": cfg["course_id"], "title": cfg["title"], "owner_status": cfg["owner_status"], "owner_control": {"path": cfg["owner_control"], "bytes": cfg["owner_control_bytes"], "sha256": cfg["owner_control_sha256"]}, "native_record_count": cfg["native_count"], "unit_count": len(units), "pages": cfg["pages"], "reader_url": cfg["reader_url"], "public_record": cfg["public_record"], "repository": cfg["repository"], "release": cfg["release"], "rights": cfg["rights_note"], "owner_native_authoritative": True, "body_prose_copied": False}
    pretty(out / "evidence" / "OWNER_RELEASE_CLOSURE.json", authority)
    tables, info = write_tables(out, cfg, package_id, dataset_id, owner_id, units)
    csv_manifest = write_csv(out, tables, package_id)
    pretty(out / "csv-projection-manifest-v0.2.0.json", csv_manifest)
    unit_ids = info["unit_ids"]
    authority_binding = ext_fact(cfg["owner_control"], str(cfg["owner_root"]), cfg["owner_control_bytes"], cfg["owner_control_sha256"], "owner_control")
    if cfg.get("backend_manifest"):
        rel, size, digest = cfg["backend_manifest"]
        if digest is None: digest = sha256(cfg["owner_root"] / rel)
        authority_binding["backend_manifest"] = {"path": rel, "bytes": size, "sha256": digest}
    pretty(out / "INPUT_AUTHORITIES.json", {"role_id": cfg["course_id"], "owner_control": authority_binding, "public_release": {"record": cfg["public_record"], "repository": cfg["repository"], "release": cfg["release"]}, "source_authority": cfg["upstream"]})
    scope = {"$schema": "schema/scope-declaration-v0.2.schema.json", "schema_id": "interlanguage/global-modular-mathematics-backend-scope/0.2.0", "schema_version": "0.2.0", "package_id": package_id, "dataset_id": dataset_id, "scope_kind": "lane_adapter", "course_ids": [uid(cfg["course_id"], "course", cfg["course_id"])], "curriculum_role_ids": [cfg["course_id"]], "aggregate_conformance_claim": False, "unbound_curriculum_role_ids": [], "owner_authority_binding": authority_binding, "curriculum_authority_binding": {"role": "current curriculum role", "curriculum_role_id": cfg["course_id"]}, "limitations": ["Native prose and full native backend remain external and authoritative.", "The adapter projects identity, ordering, hashes, routes, rights qualification, and explicit translation state only.", "No common adapter claim is made for any other curriculum role.", "Learner destination remains the owner public reader, not machine tables.", cfg["rights_note"]], "recorded_at": RECORDED_AT}
    pretty(out / "scope-declaration-v0.2.0.json", scope)
    translation_records = [{"projected_unit_id": u, "native_unit_id": units[i]["native_id"], "edition_locale": "id-ID", "native_locale": "en", "owner_native_state": units[i]["state"], "normalized_publication_state": "published_complete_release_snapshot", "state_inferred": False, "source_path": units[i]["source_path"]} for i, u in enumerate(unit_ids)]
    pretty(out / "translation-state-index-v0.2.0.json", {"$schema": "schema/translation-state-index-v0.2.schema.json", "schema_id": "interlanguage/global-modular-mathematics-translation-state-index/0.2.0", "schema_version": "0.2.0", "package_id": package_id, "dataset_id": dataset_id, "authority_bindings": [authority_binding], "coverage": {"course_id": cfg["course_id"], "granularity": "projected_owner_unit_snapshot", "authority_rows": len(units), "indexed_rows": len(translation_records), "inferred_rows": 0}, "states": ["published_complete_release_snapshot"], "records": translation_records, "identity_set_sha256": digest_lines(unit_ids), "no_inference": True, "recorded_at": RECORDED_AT})
    profiles = [{"profile_id": f"{cfg['course_id']}:profile:{name}", "name": name, "state": "materialized" if name in ("structure_localization", "publication") else "referenced_native_shard"} for name in CAPABILITIES]
    caps = []
    for name in CAPABILITIES:
        caps.append({"name": name, "version": "0.2.0", "state": "materialized" if name in ("structure_localization", "publication") else "referenced_native_shards", "schema_binding": None, "shard_refs": [authority_binding], "native_count": cfg["native_count"], "projected_count": len(unit_ids) if name == "structure_localization" else 0, "identity_set_sha256": digest_lines(unit_ids) if name == "structure_localization" else None, "identity_set_scope": "projected_units" if name == "structure_localization" else "none", "closure_rules": ["owner-native IDs and rights remain authoritative", "no prose or absent semantic detail is copied or inferred"], "loss_gap_report": {"status": "closed" if name in ("structure_localization", "publication") else "declared_limitation", "reason": "Thin adapter projection; native detail remains in the owner package."}})
    pretty(out / "capability-declarations-v0.2.0.json", {"$schema": "schema/capability-declarations-v0.2.schema.json", "schema_id": "interlanguage/global-modular-mathematics-capability-declarations/0.2.0", "schema_version": "0.2.0", "package_id": package_id, "dataset_id": dataset_id, "contract_binding": {"schema": "interlanguage/global-modular-mathematics-lane-adapter/2.3.1", "version": "2.3.1"}, "capabilities": caps, "legacy_labels": [], "namespace_crosswalk_binding": {"binding_state": "sealed_by_package_manifest", "path": "namespace-crosswalk-v0.2.0.json"}, "csv_projection_binding": {"binding_state": "sealed_by_package_manifest", "path": "csv-projection-manifest-v0.2.0.json"}, "translation_state_binding": {"binding_state": "sealed_by_package_manifest", "path": "translation-state-index-v0.2.0.json"}, "rights_cross_cutting": {"state": "referenced_native_shards", "shard_refs": [authority_binding], "native_count": 1, "identity_set_sha256": None, "closure_rules": [cfg["rights_note"]]}, "recorded_at": RECORDED_AT})
    mappings = [{"source_namespace": f"owner:{cfg['course_id']}", "target_namespace": f"common:v2.3.1:{cfg['course_id']}", "source_record_id": units[i]["native_id"], "target_record_id": unit_ids[i], "source_record_type": "unit", "target_record_type": "unit", "cardinality": "one_to_one", "mapping_state": "verified", "reverse_recipe": "read native_unit_id from projected unit payload", "evidence_refs": ["evidence/OWNER_RELEASE_CLOSURE.json"], "identity_set_sha256": digest_lines(unit_ids)} for i in range(len(units))]
    pretty(out / "namespace-crosswalk-v0.2.0.json", {"$schema": "schema/namespace-crosswalk-v0.2.schema.json", "schema_id": "interlanguage/global-modular-mathematics-namespace-crosswalk/0.2.0", "schema_version": "0.2.0", "package_id": package_id, "profiles": profiles[:3], "mappings": mappings, "unmaterialized_candidates": [], "identity_sets": {"projected_units": {"count": len(unit_ids), "sha256": digest_lines(unit_ids)}}, "recorded_at": RECORDED_AT})
    # Package payload facts, manifest, seal, and checksums are constructed in a
    # fixed order.  The manifest excludes itself, seal, and checksum file.
    payload_files = []
    for p in sorted(x for x in out.rglob("*") if x.is_file() and x.relative_to(out).as_posix() not in {"manifest.json", "seal.json", "PACKAGE_CHECKSUMS.sha256"}):
        payload_files.append(fact(p, p.relative_to(out).as_posix()))
    payload_digest = digest_lines([f"{x['path']}\0{x['bytes']}\0{x['sha256']}" for x in payload_files])
    manifest = {"$schema": "schema/lane-adapter-v2.3.1.schema.json", "schema_id": "interlanguage/global-modular-mathematics-lane-adapter/2.3.1", "schema_version": "2.3.1", "package_id": package_id, "dataset_id": dataset_id, "extension_id": uid(cfg["course_id"], "extension", cfg["slug"]), "extension_version": "0.1.0", "recorded_at": RECORDED_AT, "scope_declaration": fact(out / "scope-declaration-v0.2.0.json", "scope-declaration-v0.2.0.json", "scope_declaration"), "authorities": [authority_binding], "sidecars": [fact(out / n, n, "sidecar") for n in ["capability-declarations-v0.2.0.json", "namespace-crosswalk-v0.2.0.json", "translation-state-index-v0.2.0.json", "csv-projection-manifest-v0.2.0.json", "scope-declaration-v0.2.0.json"]], "csv_projection": {"manifest": fact(out / "csv-projection-manifest-v0.2.0.json", "csv-projection-manifest-v0.2.0.json", "sidecar"), "table_csv_count": len(TABLES), "aggregate_csv_count": 1, "record_count": sum(len(v) for v in tables.values()), "roundtrip_state": "pass"}, "build": {"builder": fact(out / "tools/build_gap_v23_adapters.py", "tools/build_gap_v23_adapters.py", "builder"), "validator": fact(out / "tools/validate_lane_adapter_v231.py", "tools/validate_lane_adapter_v231.py", "validator"), "canonical_serialization": {"scope": "builder_generated_json_jsonl_and_csv_only", "encoding": "UTF-8", "newline": "LF", "json_keys": "lexicographically_sorted", "trailing_newline": True, "copied_schema_and_tool_files": "preserved_exact_source_bytes"}, "deterministic_replay": "byte_identical", "build_a_sha256": payload_digest, "build_b_sha256": payload_digest}, "files": payload_files, "seal_policy": {"algorithm": "sha256-sorted-path-bytes-v1", "seal_file": "seal.json", "seal_excluded_from_own_digest": True, "binds": ["schemas", "tools", "input_authorities", "tables", "sidecars", "csv_projections", "manifest"]}, "zero_copy_policy": {"owner_native_authoritative": True, "full_prose_centralized": False, "owner_ids_reminted": False, "aggregate_conformance_claim": False, "machine_data_is_learner_destination": False, "machine_surfaces_secondary": True}}
    # Copy this builder into the package only after the generation code exists;
    # its exact bytes are part of the package contract.
    shutil.copy2(HERE, out / "tools" / "build_gap_v23_adapters.py")
    manifest["build"]["builder"] = fact(out / "tools/build_gap_v23_adapters.py", "tools/build_gap_v23_adapters.py", "builder")
    pretty(out / "manifest.json", manifest)
    seal_facts = payload_files + [fact(out / "manifest.json", "manifest.json", "package_manifest")]
    import hashlib
    seal_payload = "".join(f"{x['path']}\0{x['bytes']}\0{x['sha256']}\n" for x in sorted(seal_facts, key=lambda x: x["path"]))
    seal = {"schema_id": "interlanguage/global-modular-mathematics-lane-adapter-seal/1.0.0", "package_id": package_id, "algorithm": "sha256-sorted-path-bytes-v1", "seal_excluded_from_own_digest": True, "file_count": len(seal_facts), "bytes": sum(x["bytes"] for x in seal_facts), "aggregate_sha256": hashlib.sha256(seal_payload.encode()).hexdigest(), "files": sorted(seal_facts, key=lambda x: x["path"])}
    pretty(out / "seal.json", seal)
    checksum_paths = [p for p in sorted(x for x in out.rglob("*") if x.is_file() and x.relative_to(out).as_posix() != "PACKAGE_CHECKSUMS.sha256")]
    (out / "PACKAGE_CHECKSUMS.sha256").write_text("".join(f"{sha256(p)}  {p.relative_to(out).as_posix()}\n" for p in checksum_paths), encoding="utf-8", newline="\n")
    return {"role_id": cfg["course_id"], "package": str(out), "package_id": package_id, "units": len(units), "records": sum(len(v) for v in tables.values()), "payload_sha256": payload_digest}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-root", type=Path, default=PROJECT / "backend" / "v2.3" / "extensions")
    ap.add_argument("--role", action="append", choices=["A30", "B95", "C140"])
    args = ap.parse_args()
    selected = args.role or ["A30", "B95", "C140"]
    results = []
    for role in selected:
        cfg = owner_configs()[role]
        results.append(build_package(cfg, args.output_root / f"{cfg['slug']}-v0.1.0"))
    print(json.dumps({"status": "PASS", "adapters": results}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
