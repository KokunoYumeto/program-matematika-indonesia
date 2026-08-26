#!/usr/bin/env python3
"""Build the evidence/planning federation that sits beside the curriculum backend.

The package intentionally does not copy owner-native mathematics backends.  It
serves exact language profiles, bounded bridge claims, accessibility work,
course-level resource pointers, and the explicit state of the active compute
study.  Empty future research tables are declared in table_statuses but are not
materialized as empty files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import uuid
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
WORKSPACE = REPO.parents[2]
DOSSIER = WORKSPACE / "01_methodology/research_department/marginal_intelligibility_reach_20260816"
ACTIVE_STUDY = WORKSPACE / "01_methodology/research_department/ai_compute_educational_access_20260825"
CENTRAL_V1 = REPO / "backend/v1/program-matematika-indonesia-v0.51.2/backend.json"
NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
DATASET_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0.0"
RECORDED_AT = "2026-08-25T00:40:00+02:00"

MATERIALIZED = [
    "research_projects",
    "research_workstreams",
    "language_profiles",
    "recommendations",
    "bridge_surfaces",
    "accessibility_interventions",
    "manager_coverage",
    "evidence_sources",
    "asset_sources",
    "curriculum_resources",
]

PLANNED = {
    "population_cells": "active_research_unmaterialized",
    "curriculum_unit_mappings": "active_research_unmaterialized",
    "compute_observations": "active_research_unmaterialized",
    "cost_scenarios": "active_research_unmaterialized",
    "ranking_runs": "active_research_unmaterialized",
    "ranking_items": "active_research_unmaterialized",
    "impact_snapshots": "active_research_unmaterialized",
}

README_TEXT = """# Educational-access research federation

This additive package lets the modular curriculum backend serve the existing
educational-access and marginal-intelligibility research without pretending
that research records are mathematics course units. It contains 490 typed,
stable records across ten materialized tables, with lossless JSONL and CSV
projections, exact source facts, foreign-key checks, and a public compact JSON
projection at `docs/data/educational-access.json`.

Seven future tables are deliberately declared but not emitted: population
cells, curriculum-unit mappings, compute observations, cost scenarios, ranking
runs, ranking items, and impact snapshots. Their absence means “active research
not yet materialized,” never zero evidence or a fabricated result.

The package is a frozen release snapshot. The validator always verifies its
schema, manifest, hashes, UUIDv5 identities, projections, foreign keys, public
catalog, and portable public asset locators. It also reports whether the current
mutable workspace still matches the captured source facts. Use
`--require-live-source-replay` immediately after rebuilding when that stronger
current-workspace equality is required; a later source change does not
retroactively invalidate an already frozen package.

```powershell
python -B scripts/build-educational-access-federation-v1.py
python -B scripts/validate-educational-access-federation-v1.py --require-live-source-replay
```
"""

PAYLOAD_FIELDS: dict[str, dict[str, str]] = {
    "research_projects": {
        "project_key": "str", "title": "str", "research_state": "str",
        "scope_note": "str", "source_root": "str", "source_inventory_sha256": "sha",
        "required_outputs": "array_str", "public_boundary": "str",
    },
    "research_workstreams": {
        "workstream_key": "str", "project_key": "str", "title": "str",
        "research_state": "str", "record_count": "int", "public_boundary": "str",
        "source_artifacts": "array_str",
    },
    "language_profiles": {
        "profile_id": "str", "lane": "str", "region": "str", "target_profile": "str",
        "tag": "str", "script_or_orthography": "str", "likely_reader_cohort": "str",
        "local_status": "str", "sequence_state": "str", "g_id": "str", "g_src": "str",
        "g_use": "str", "g_audit": "str", "g_tech": "str", "g_harm": "str",
        "R": "str", "S": "str", "A": "str", "N": "str", "V": "str",
        "P": "str", "F": "str", "D": "str", "confidence": "str",
        "evidence_ids": "array_str", "asset_ids": "array_str", "decision_caveat": "str",
    },
    "recommendations": {
        "lane_order": "int", "lane": "str", "wave": "str", "profile_id": "str",
        "profile_record_id": "urn_or_null", "target": "str", "openlogic_recommendation": "str",
        "selection_basis": "str", "minimum_preparation": "str",
        "open_preparation_fields": "array_str", "confidence": "str",
        "evidence_ids": "array_str", "asset_ids": "array_str", "production_authority": "str",
    },
    "bridge_surfaces": {
        "bridge_id": "str", "kind": "str", "local_surface": "str", "status": "str",
        "script_orthography": "str", "plausible_communities": "str",
        "comprehension_without_prior_study": "str", "direct_evidence": "str",
        "overlap_with_existing_editions": "str", "unique_displaced_or_diaspora_value": "str",
        "explicitly_not_served": "str", "coverage_credit": "str",
        "evidence_ids": "array_str", "asset_ids": "array_str", "decision": "str",
    },
    "accessibility_interventions": {
        "axis_id": "str", "access_axis": "str", "target_users": "str",
        "required_output": "str", "marginal_access_mechanism": "str",
        "current_local_state": "str", "minimum_gate": "str",
        "evidence_ids": "array_str", "asset_ids": "array_str", "priority": "str", "caveat": "str",
    },
    "manager_coverage": {
        "manager": "str", "project_or_target": "str", "exact_variety_or_scope": "str",
        "classification": "str", "classification_scope": "str", "current_evidence": "str",
        "overlap_credit": "str", "critical_caveat": "str", "asset_ids": "array_str",
    },
    "evidence_sources": {
        "evidence_id": "str", "title": "str", "authority": "str", "url": "str",
        "accessed_utc": "str", "supports": "str", "limitations": "str",
        "scope_tags": "array_str",
    },
    "asset_sources": {
        "asset_id": "str", "path": "str", "bytes": "int", "mtime_utc": "str",
        "sha256": "sha", "provenance": "str", "role": "str",
        "variety_tags": "array_str", "claim_boundary": "str",
    },
    "curriculum_resources": {
        "course_key": "str", "title": "str", "stage": "str", "course_state": "str",
        "scope": "str", "outcome": "str", "prerequisite_course_keys": "array_str",
        "owner_lane": "str", "selected_resource_title": "str",
        "learner_start_url": "str_or_null", "repository_url": "str_or_null",
        "zenodo_url": "str_or_null", "archive_url": "str_or_null",
        "baseline_family": "str", "unit_mapping_state": "str",
    },
}

RECORD_TYPES = {
    "research_projects": "research_project",
    "research_workstreams": "research_workstream",
    "language_profiles": "language_profile",
    "recommendations": "recommendation",
    "bridge_surfaces": "bridge_surface",
    "accessibility_interventions": "accessibility_intervention",
    "manager_coverage": "manager_coverage",
    "evidence_sources": "evidence_source",
    "asset_sources": "asset_source",
    "curriculum_resources": "curriculum_resource",
}


def canonical(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_fact(path: Path, role: str) -> dict[str, Any]:
    data = path.read_bytes()
    try:
        rel = path.relative_to(WORKSPACE).as_posix()
    except ValueError:
        rel = path.relative_to(REPO).as_posix()
    return {"path": rel, "bytes": len(data), "sha256": sha_bytes(data), "role": role}


def split_ids(value: str) -> list[str]:
    return [item.strip() for item in value.replace(",", ";").split(";") if item.strip()]


def public_asset_locator(value: str, digest: str) -> str:
    normalized = value.strip().replace("\\", "/")
    workspace_prefix = WORKSPACE.resolve().as_posix().rstrip("/") + "/"
    if normalized.casefold().startswith(workspace_prefix.casefold()):
        relative = normalized[len(workspace_prefix):]
        parts = [part for part in relative.split("/") if part]
        if parts and all(part not in {".", ".."} for part in parts):
            return "workspace:///" + "/".join(parts)
    return f"external-source://sha256/{digest.lower()}"


def stable_id(record_type: str, stable_key: str) -> str:
    return f"urn:uuid:{uuid.uuid5(NAMESPACE, record_type + ':' + stable_key)}"


def record(table: str, stable_key: str, status: str, payload: dict[str, Any], source: dict[str, Any], row: int) -> dict[str, Any]:
    record_type = RECORD_TYPES[table]
    return {
        "record_type": record_type,
        "id": stable_id(record_type, stable_key),
        "stable_key": stable_key,
        "status": status,
        "recorded_at": RECORDED_AT,
        "source_file": source["path"],
        "source_sha256": source["sha256"],
        "source_row": row,
        "payload": payload,
    }


def read_csv(name: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    path = DOSSIER / name
    fact = file_fact(path, "completed_research_dataset")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle)), fact


def type_schema(kind: str) -> dict[str, Any]:
    if kind == "str":
        return {"type": "string"}
    if kind == "int":
        return {"type": "integer"}
    if kind == "sha":
        return {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    if kind == "array_str":
        return {"type": "array", "items": {"type": "string"}}
    if kind == "str_or_null":
        return {"type": ["string", "null"]}
    if kind == "urn_or_null":
        return {"type": ["string", "null"], "pattern": "^urn:uuid:[0-9a-f-]{36}$"}
    raise ValueError(kind)


def make_schema() -> dict[str, Any]:
    defs: dict[str, Any] = {}
    table_properties: dict[str, Any] = {}
    for table, fields in PAYLOAD_FIELDS.items():
        record_type = RECORD_TYPES[table]
        definition = f"{record_type}_record"
        defs[definition] = {
            "type": "object",
            "additionalProperties": False,
            "required": ["record_type", "id", "stable_key", "status", "recorded_at", "source_file", "source_sha256", "source_row", "payload"],
            "properties": {
                "record_type": {"const": record_type},
                "id": {"type": "string", "pattern": "^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"},
                "stable_key": {"type": "string", "minLength": 1},
                "status": {"type": "string", "minLength": 1},
                "recorded_at": {"type": "string", "format": "date-time"},
                "source_file": {"type": "string", "minLength": 1},
                "source_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "source_row": {"type": "integer", "minimum": 0},
                "payload": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": list(fields),
                    "properties": {name: type_schema(kind) for name, kind in fields.items()},
                },
            },
        }
        table_properties[table] = {"type": "array", "items": {"$ref": f"#/$defs/{definition}"}}

    defs["source_fact"] = {
        "type": "object", "additionalProperties": False,
        "required": ["path", "bytes", "sha256", "role"],
        "properties": {
            "path": {"type": "string"}, "bytes": {"type": "integer", "minimum": 0},
            "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}, "role": {"type": "string"},
        },
    }
    defs["table_status"] = {
        "type": "object", "additionalProperties": False,
        "required": ["table_name", "status", "materialized", "record_count", "notes"],
        "properties": {
            "table_name": {"type": "string"}, "status": {"type": "string"},
            "materialized": {"type": "boolean"}, "record_count": {"type": "integer", "minimum": 0},
            "notes": {"type": "string"},
        },
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://kokunoyumeto.github.io/program-matematika-indonesia/schema/educational-access-federation-v1.schema.json",
        "title": "Educational access evidence and planning federation v1",
        "type": "object", "additionalProperties": False,
        "required": ["$schema", "schema_name", "schema_version", "dataset_id", "dataset_version", "recorded_at", "source_facts", "table_statuses", "tables"],
        "properties": {
            "$schema": {"const": "schema/educational-access-federation-v1.schema.json"},
            "schema_name": {"const": "interlanguage-educational-access-federation"},
            "schema_version": {"const": SCHEMA_VERSION},
            "dataset_id": {"type": "string", "pattern": "^urn:uuid:[0-9a-f-]{36}$"},
            "dataset_version": {"const": DATASET_VERSION},
            "recorded_at": {"type": "string", "format": "date-time"},
            "source_facts": {"type": "array", "items": {"$ref": "#/$defs/source_fact"}},
            "table_statuses": {"type": "array", "items": {"$ref": "#/$defs/table_status"}},
            "tables": {"type": "object", "additionalProperties": False, "required": MATERIALIZED, "properties": table_properties},
        },
        "$defs": defs,
    }


def build_records() -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], list[dict[str, Any]]]:
    source_facts: list[dict[str, Any]] = []
    fact_by_name: dict[str, dict[str, Any]] = {}
    for name, role in [
        ("GLOBAL_GAP_REGISTER.csv", "language_profile_seed"),
        ("RANKED_RECOMMENDATIONS.csv", "recommendation_seed"),
        ("INTERLANGUAGE_OVERLAP_MATRIX.csv", "interlanguage_evidence"),
        ("ACCESSIBILITY_GAP_REGISTER.csv", "accessibility_evidence"),
        ("MANAGER_COVERAGE_REGISTER.csv", "existing_work_coverage"),
        ("EVIDENCE_REGISTER.jsonl", "evidence_ledger"),
        ("ASSET_CENSUS.jsonl", "asset_ledger"),
        ("DOSSIER.md", "completed_research_narrative"),
        ("SCORING_MODEL.md", "completed_scoring_model"),
        ("FORMALISM_CROSSWALK.md", "completed_formalism_crosswalk"),
    ]:
        fact = file_fact(DOSSIER / name, role)
        source_facts.append(fact)
        fact_by_name[name] = fact
    for name, role in [
        ("MODEL_SPEC.md", "active_study_model"),
        ("SEARCH_PROTOCOL.md", "active_study_method"),
    ]:
        fact = file_fact(ACTIVE_STUDY / name, role)
        source_facts.append(fact)
        fact_by_name[f"active/{name}"] = fact
    central_fact = file_fact(CENTRAL_V1, "current_curriculum_catalog")
    source_facts.append(central_fact)

    dossier_inventory = sha_bytes(canonical(sorted((f["path"], f["bytes"], f["sha256"]) for f in source_facts if "marginal_intelligibility" in f["path"])))
    active_inventory = sha_bytes(canonical(sorted((f["path"], f["bytes"], f["sha256"]) for f in source_facts if "ai_compute_educational_access" in f["path"])))

    tables: dict[str, list[dict[str, Any]]] = {name: [] for name in MATERIALIZED}
    projects = [
        {
            "project_key": "marginal-intelligibility-reach-20260816",
            "title": "Marginal Intelligibility Reach",
            "research_state": "completed_source_audited_seed",
            "scope_note": "Evidence-bounded global gap, bridge-overlap, accessibility, and recommendation registers; no blanket interlanguage coverage.",
            "source_root": DOSSIER.relative_to(WORKSPACE).as_posix(),
            "source_inventory_sha256": dossier_inventory,
            "required_outputs": ["language profiles", "ranked seed recommendations", "bridge overlap", "accessibility gaps", "evidence ledger"],
            "public_boundary": "Completed registers and sanitized evidence only; raw user messages and internal control state are excluded.",
        },
        {
            "project_key": "ai-compute-educational-access-20260825",
            "title": "AI Compute for Global Educational Access",
            "research_state": "active_research",
            "scope_note": "Exact population cells, OpenStax and Open Logic unit mapping, compute/cost scenarios, deduplicated portfolios, accessibility formats, and a cited paper.",
            "source_root": ACTIVE_STUDY.relative_to(WORKSPACE).as_posix(),
            "source_inventory_sha256": active_inventory,
            "required_outputs": ["population cells", "curriculum unit mappings", "compute observations", "cost scenarios", "Top 10", "Top 100", "PAPER.md", "PAPER.docx", "PAPER.pdf"],
            "public_boundary": "Only the active model, workstream status, and populated predecessor registers are served; unpublished active-study results are not invented or imported.",
        },
    ]
    for idx, payload in enumerate(projects, 1):
        source = fact_by_name["DOSSIER.md"] if idx == 1 else fact_by_name["active/MODEL_SPEC.md"]
        tables["research_projects"].append(record("research_projects", payload["project_key"], payload["research_state"], payload, source, 0))

    workstreams = [
        ("gap-register", "marginal-intelligibility-reach-20260816", "Exact variety/script/territory/cohort gap register", "completed_seed", 169, "Serves the completed 169-profile register; values are opportunity bands, not final population counts.", ["GLOBAL_GAP_REGISTER.csv"]),
        ("recommendation-seed", "marginal-intelligibility-reach-20260816", "Ranked intervention seed", "completed_seed", 94, "Serves 94 bounded recommendations; not the active study's final Top 10/100.", ["RANKED_RECOMMENDATIONS.csv"]),
        ("interlanguage-overlap", "ai-compute-educational-access-20260825", "Evidence-bounded interlanguage overlap", "seed_complete_active_refinement", 14, "Coverage remains zero where exact-surface comprehension evidence is absent.", ["INTERLANGUAGE_OVERLAP_MATRIX.csv", "MODEL_SPEC.md"]),
        ("population-cells", "ai-compute-educational-access-20260825", "Exact population and learner cells", "active_unmaterialized", 0, "Awaiting primary-source population ranges and explicit non-overlap; no numbers are fabricated.", ["MODEL_SPEC.md"]),
        ("curriculum-unit-mapping", "ai-compute-educational-access-20260825", "OpenStax and Open Logic unit mapping", "active_unmaterialized", 0, "Course-level resources are served now; unit-level population mappings remain active research.", ["MODEL_SPEC.md", "backend-v1/program-matematika-indonesia-v0.51.2/backend.json"]),
        ("compute-cost-scenarios", "ai-compute-educational-access-20260825", "Compute, token, build, and cost scenarios", "active_unmaterialized", 0, "Gross, cached, uncached, and output tokens must remain separate.", ["MODEL_SPEC.md"]),
        ("portfolio-top-10", "ai-compute-educational-access-20260825", "Deduplicated Top 10 intervention portfolio", "active_unmaterialized", 0, "Will recompute overlap after every selected intervention.", ["MODEL_SPEC.md"]),
        ("portfolio-top-100", "ai-compute-educational-access-20260825", "Deduplicated Top 100 intervention portfolio", "active_unmaterialized", 0, "Will expose sensitivity and stability, not false precision.", ["MODEL_SPEC.md"]),
        ("accessibility-formats", "ai-compute-educational-access-20260825", "Accessibility-format interventions", "seed_complete_active_refinement", 14, "Accessibility is an independent intervention axis, not a translation footnote.", ["ACCESSIBILITY_GAP_REGISTER.csv", "MODEL_SPEC.md"]),
        ("research-paper", "ai-compute-educational-access-20260825", "Cited research paper and implementation scenarios", "active_unmaterialized", 0, "The paper remains in the research task until source, model, and visual validation close.", ["MODEL_SPEC.md", "SEARCH_PROTOCOL.md"]),
    ]
    work_source = fact_by_name["active/MODEL_SPEC.md"]
    for idx, item in enumerate(workstreams, 1):
        key, project_key, title, state, count, boundary, artifacts = item
        payload = {"workstream_key": key, "project_key": project_key, "title": title, "research_state": state, "record_count": count, "public_boundary": boundary, "source_artifacts": artifacts}
        tables["research_workstreams"].append(record("research_workstreams", key, state, payload, work_source, idx))

    rows, gap_fact = read_csv("GLOBAL_GAP_REGISTER.csv")
    profile_ids: dict[str, str] = {}
    for rownum, row in enumerate(rows, 2):
        refs = split_ids(row["evidence_ids"])
        payload = {name: row[name] for name in PAYLOAD_FIELDS["language_profiles"] if name not in {"evidence_ids", "asset_ids"}}
        payload["evidence_ids"] = [item for item in refs if item.startswith("MIR-E")]
        payload["asset_ids"] = [item for item in refs if item.startswith("MIR-A")]
        rec = record("language_profiles", row["profile_id"], row["local_status"], payload, gap_fact, rownum)
        profile_ids[row["profile_id"]] = rec["id"]
        tables["language_profiles"].append(rec)

    rows, rec_fact = read_csv("RANKED_RECOMMENDATIONS.csv")
    for rownum, row in enumerate(rows, 2):
        payload = {
            "lane_order": int(row["lane_order"]), "lane": row["lane"], "wave": row["wave"],
            "profile_id": row["profile_id"], "profile_record_id": profile_ids.get(row["profile_id"]),
            "target": row["target"], "openlogic_recommendation": row["openlogic_recommendation"],
            "selection_basis": row["selection_basis"], "minimum_preparation": row["minimum_preparation"],
            "open_preparation_fields": split_ids(row["open_preparation_fields"]),
            "confidence": row["confidence"],
            "evidence_ids": [item for item in split_ids(row["evidence_ids"]) if item.startswith("MIR-E")],
            "asset_ids": [item for item in split_ids(row["evidence_ids"]) if item.startswith("MIR-A")],
            "production_authority": row["production_authority"],
        }
        tables["recommendations"].append(record("recommendations", f"recommendation:{row['lane_order']}:{row['profile_id']}", "seed_not_final_portfolio", payload, rec_fact, rownum))

    rows, bridge_fact = read_csv("INTERLANGUAGE_OVERLAP_MATRIX.csv")
    for rownum, row in enumerate(rows, 2):
        refs = split_ids(row["evidence_ids"])
        payload = {name: row[name] for name in PAYLOAD_FIELDS["bridge_surfaces"] if name not in {"evidence_ids", "asset_ids"}}
        payload["evidence_ids"] = [item for item in refs if item.startswith("MIR-E")]
        payload["asset_ids"] = [item for item in refs if not item.startswith("MIR-E")]
        tables["bridge_surfaces"].append(record("bridge_surfaces", row["bridge_id"], row["status"], payload, bridge_fact, rownum))

    rows, access_fact = read_csv("ACCESSIBILITY_GAP_REGISTER.csv")
    for rownum, row in enumerate(rows, 2):
        refs = split_ids(row["evidence_ids"])
        payload = {name: row[name] for name in PAYLOAD_FIELDS["accessibility_interventions"] if name not in {"evidence_ids", "asset_ids"}}
        payload["evidence_ids"] = [item for item in refs if item.startswith("MIR-E")]
        payload["asset_ids"] = [item for item in refs if item.startswith("MIR-A")]
        tables["accessibility_interventions"].append(record("accessibility_interventions", row["axis_id"], "seed_complete_active_refinement", payload, access_fact, rownum))

    rows, manager_fact = read_csv("MANAGER_COVERAGE_REGISTER.csv")
    for rownum, row in enumerate(rows, 2):
        key = f"{row['manager']}:{rownum - 1:03d}"
        payload = {name: row[name] for name in PAYLOAD_FIELDS["manager_coverage"] if name != "asset_ids"}
        payload["asset_ids"] = split_ids(row["asset_ids"])
        tables["manager_coverage"].append(record("manager_coverage", key, row["classification"], payload, manager_fact, rownum))

    evidence_fact = fact_by_name["EVIDENCE_REGISTER.jsonl"]
    with (DOSSIER / "EVIDENCE_REGISTER.jsonl").open("r", encoding="utf-8") as handle:
        for rownum, line in enumerate(handle, 1):
            if not line.strip():
                continue
            payload = json.loads(line)
            tables["evidence_sources"].append(record("evidence_sources", payload["evidence_id"], "source_recorded", payload, evidence_fact, rownum))

    asset_fact = fact_by_name["ASSET_CENSUS.jsonl"]
    with (DOSSIER / "ASSET_CENSUS.jsonl").open("r", encoding="utf-8") as handle:
        for rownum, line in enumerate(handle, 1):
            if not line.strip():
                continue
            payload = json.loads(line)
            payload["sha256"] = payload["sha256"].lower()
            payload["path"] = public_asset_locator(payload["path"], payload["sha256"])
            tables["asset_sources"].append(record("asset_sources", payload["asset_id"], "asset_recorded", payload, asset_fact, rownum))

    central = json.loads(CENTRAL_V1.read_text(encoding="utf-8"))
    resource_by_key = {row["resource_key"]: row for row in central["tables"]["resources"]}
    for rownum, course in enumerate(sorted(central["tables"]["courses"], key=lambda item: item["course_key"]), 1):
        resource = resource_by_key[course["resource_keys"][0]]
        ext = resource.get("extensions", {}).get("interlanguage.curriculum-selection", {})
        title = resource["original_title"]
        lower = title.lower()
        family = "openstax" if "openstax" in lower else "open_logic_project" if "open logic" in lower else "other_open_mathematics"
        payload = {
            "course_key": course["course_key"], "title": course["title"], "stage": course["stage"],
            "course_state": course["status"], "scope": course["scope"], "outcome": course["outcome"],
            "prerequisite_course_keys": course["prerequisite_course_keys"],
            "owner_lane": course.get("extensions", {}).get("interlanguage.curriculum-owner", {}).get("owner_lane", ""),
            "selected_resource_title": title,
            "learner_start_url": ext.get("learner_start_url") or resource.get("official_reader") or None,
            "repository_url": resource.get("official_repository") or None,
            "zenodo_url": ext.get("zenodo") or None,
            "archive_url": ext.get("archive_url") or None,
            "baseline_family": family,
            "unit_mapping_state": "active_research_unmaterialized" if family in {"openstax", "open_logic_project"} else "out_of_current_unit_mapping_baseline",
        }
        tables["curriculum_resources"].append(record("curriculum_resources", course["course_key"], course["status"], payload, central_fact, rownum))

    for rows in tables.values():
        rows.sort(key=lambda item: item["stable_key"])
    table_statuses = [
        {"table_name": name, "status": "materialized", "materialized": True, "record_count": len(tables[name]), "notes": "Canonical JSONL and lossless CSV projections are present."}
        for name in MATERIALIZED
    ]
    table_statuses.extend(
        {"table_name": name, "status": state, "materialized": False, "record_count": 0, "notes": "Declared for the active research task; no empty projection is emitted and no values are fabricated."}
        for name, state in PLANNED.items()
    )
    return tables, source_facts, table_statuses


def safe_replace_dir(path: Path) -> None:
    resolved = path.resolve()
    allowed = (REPO / "backend/research").resolve()
    temp_allowed = (REPO / "tmp").resolve()
    if not (resolved.is_relative_to(allowed) or resolved.is_relative_to(temp_allowed)):
        raise RuntimeError(f"refusing to replace output outside bounded roots: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True, exist_ok=True)


def write_package(package_root: Path, public_json: Path, schema_path: Path) -> None:
    tables, source_facts, table_statuses = build_records()
    schema = make_schema()
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_bytes(canonical(schema))
    safe_replace_dir(package_root)
    (package_root / "data").mkdir()
    (package_root / "csv").mkdir()
    (package_root / "schema").mkdir()
    (package_root / "README.md").write_text(README_TEXT, encoding="utf-8", newline="\n")
    (package_root / "schema/educational-access-federation-v1.schema.json").write_bytes(canonical(schema))

    package = {
        "$schema": "schema/educational-access-federation-v1.schema.json",
        "schema_name": "interlanguage-educational-access-federation",
        "schema_version": SCHEMA_VERSION,
        "dataset_id": stable_id("dataset", "educational-access-federation"),
        "dataset_version": DATASET_VERSION,
        "recorded_at": RECORDED_AT,
        "source_facts": sorted(source_facts, key=lambda item: item["path"]),
        "table_statuses": sorted(table_statuses, key=lambda item: item["table_name"]),
        "tables": tables,
    }
    (package_root / "federation.json").write_bytes(canonical(package))

    all_records: list[dict[str, Any]] = []
    for table in MATERIALIZED:
        rows = tables[table]
        all_records.extend(rows)
        with (package_root / "data" / f"{table}.jsonl").open("wb") as handle:
            for row in rows:
                handle.write(canonical(row))
        with (package_root / "csv" / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["id", "stable_key", "status", "recorded_at", "source_file", "source_sha256", "source_row", "record_json"],
                lineterminator="\n",
            )
            writer.writeheader()
            for row in rows:
                writer.writerow({
                    "id": row["id"], "stable_key": row["stable_key"], "status": row["status"],
                    "recorded_at": row["recorded_at"], "source_file": row["source_file"],
                    "source_sha256": row["source_sha256"], "source_row": row["source_row"],
                    "record_json": json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
                })
    all_records.sort(key=lambda item: (item["record_type"], item["stable_key"]))
    with (package_root / "records.jsonl").open("wb") as handle:
        for row in all_records:
            handle.write(canonical(row))
    with (package_root / "records.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["record_type", "id", "stable_key", "status", "record_json"],
            lineterminator="\n",
        )
        writer.writeheader()
        for row in all_records:
            writer.writerow({"record_type": row["record_type"], "id": row["id"], "stable_key": row["stable_key"], "status": row["status"], "record_json": json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":"))})

    public = {
        "schemaVersion": SCHEMA_VERSION,
        "datasetVersion": DATASET_VERSION,
        "recordedAt": RECORDED_AT,
        "summary": {name: len(tables[name]) for name in MATERIALIZED},
        "researchProjects": [{"id": row["id"], **row["payload"]} for row in tables["research_projects"]],
        "workstreams": [{"id": row["id"], **row["payload"]} for row in tables["research_workstreams"]],
        "profiles": [{"id": row["id"], **row["payload"]} for row in tables["language_profiles"]],
        "recommendations": [{"id": row["id"], **row["payload"]} for row in tables["recommendations"]],
        "bridges": [{"id": row["id"], **row["payload"]} for row in tables["bridge_surfaces"]],
        "accessibility": [{"id": row["id"], **row["payload"]} for row in tables["accessibility_interventions"]],
        "curriculum": [{"id": row["id"], **row["payload"]} for row in tables["curriculum_resources"]],
        "plannedTables": [row for row in table_statuses if not row["materialized"]],
        "method": {
            "impactModel": "population range × comfort/access × scarcity × non-overlap × accessibility",
            "computeModel": "EMA_cik = N_c × D_ck × C_ci × P_ci × U_ci × R_ck",
            "readinessGates": ["G-ID", "G-SRC", "G-USE", "G-AUDIT", "G-TECH", "G-HARM"],
            "coverageRule": "No interlanguage receives blanket regional credit; exact surface, cohort, script, evidence, overlap, and exclusions are required.",
            "rankingBoundary": "The 94 recommendations are a completed seed register. The active study's deduplicated Top 10 and Top 100 are not yet populated.",
        },
        "downloads": {
            "federation": "https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia/main/backend/research/educational-access-v0.1.0/federation.json",
            "recordsJsonl": "https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia/main/backend/research/educational-access-v0.1.0/records.jsonl",
            "recordsCsv": "https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia/main/backend/research/educational-access-v0.1.0/records.csv",
        },
    }
    public_json.parent.mkdir(parents=True, exist_ok=True)
    public_json.write_bytes(canonical(public))
    (package_root / "public-catalog.json").write_bytes(canonical(public))

    files = []
    for path in sorted(package_root.rglob("*")):
        if path.is_file() and path.name not in {"README.md", "manifest.json"}:
            data = path.read_bytes()
            files.append({"path": path.relative_to(package_root).as_posix(), "bytes": len(data), "sha256": sha_bytes(data)})
    manifest = {
        "schema_id": "interlanguage/educational-access-federation-manifest/v1",
        "dataset_version": DATASET_VERSION,
        "recorded_at": RECORDED_AT,
        "record_count": len(all_records),
        "table_counts": {name: len(tables[name]) for name in MATERIALIZED},
        "files": files,
    }
    (package_root / "manifest.json").write_bytes(canonical(manifest))
    print(json.dumps({"result": "built", "package": str(package_root), "records": len(all_records), "tables": manifest["table_counts"], "public_json": str(public_json)}, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, default=REPO / "backend/research/educational-access-v0.1.0")
    parser.add_argument("--public-json", type=Path, default=REPO / "docs/data/educational-access.json")
    parser.add_argument("--schema-path", type=Path, default=REPO / "schemas/educational-access-federation-v1.schema.json")
    args = parser.parse_args()
    write_package(args.package_root.resolve(), args.public_json.resolve(), args.schema_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
