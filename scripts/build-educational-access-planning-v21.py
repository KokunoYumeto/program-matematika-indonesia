#!/usr/bin/env python3
"""Materialize the educational-access planning layer for backend v2.1.

The research dossier remains the read-only authority.  This adapter turns its
curriculum, adaptation, accessibility, and compute tables into deterministic
typed JSONL without copying corpus prose or population-level research data.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]
EXTERNAL_SOURCE = WORKSPACE / "01_methodology/research_department/ai_compute_educational_access_20260825"
OUT = ROOT / "backend/v2.1/planning/educational-access"
AUTHORITY_SNAPSHOT = OUT / "authority_snapshot.json"
SCHEMA_ID = "interlanguage/global-backend-v2.1-educational-access-planning/0.1.0"
RECORDED_AT = "2026-08-26T00:00:00Z"

EXPECTED = {
    "MODEL_SPEC.md": (8522, "0d7254c61152dcb1207aa2aa0eec1ddf2599efb23631c9c2b6276005bb4c96ed"),
    "curriculum_units.csv": (7074, "0f7a958d7c19f989a1c95f673456b3667ed23f41b64208100ea1cb5c3360e204"),
    "curriculum_portfolios.csv": (3404, "2e4cc460c4cb343a092c5a8a4c11ec09eef091a93807d983b74e258a698b5049"),
    "adaptation_depths.csv": (1206, "1e4986b6da27b3aa8b901a41205e28945b253a6b5e5d838c2efe0c4171b2492c"),
    "accessibility_derivatives.csv": (1743, "34eed02a5642bd1d9a205f5751f39c3f7d1f0795979e180e05296c51e6d34fb9"),
    "compute_assumptions.csv": (1520, "5b3f31549a9c8e8f2c94e9fe5e8072464b1c20b914c9ee522901699abac79771"),
    "compute_scenarios.csv": (1069, "a050b2d8ff42b4a60cd500dbc2a871e7c44760e06a296ce6f5fc803b7f7fa444"),
    "ASSET_CENSUS.jsonl": (171459, "e36a07a1e3a23f74e489788f0906fe06a3fcd27974a4238855f5624a76e2ec44"),
    "EVIDENCE_REGISTER.jsonl": (65123, "11862f45184dbdaead27d84a23e25e262c17c8e792896bcdb1bd896a4a2bdc76"),
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text("".join(canonical(row) + "\n" for row in rows), encoding="utf-8", newline="\n")


def read_csv_path(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_or_load_authority_snapshot() -> dict[str, Any]:
    """Freeze only the planning rows and ten register rows this adapter uses."""

    table_names = [
        "curriculum_units.csv",
        "curriculum_portfolios.csv",
        "adaptation_depths.csv",
        "accessibility_derivatives.csv",
        "compute_assumptions.csv",
        "compute_scenarios.csv",
    ]
    if EXTERNAL_SOURCE.is_dir():
        for name, (expected_bytes, expected_sha) in EXPECTED.items():
            path = EXTERNAL_SOURCE / name
            actual = (path.stat().st_size, sha256_path(path)) if path.is_file() else None
            if actual != (expected_bytes, expected_sha):
                raise ValueError(f"planning upstream authority changed: {name}: {actual}")
        tables = {name: read_csv_path(EXTERNAL_SOURCE / name) for name in table_names}
        source_ids = {
            source_id
            for name in ("curriculum_units.csv", "curriculum_portfolios.csv", "compute_scenarios.csv")
            for row in tables[name]
            for field in ("source_id", "source_ids")
            for source_id in refs(row.get(field, ""))
        }
        selected_register_rows = []
        resolved_ids: set[str] = set()
        for name, key in (("ASSET_CENSUS.jsonl", "asset_id"), ("EVIDENCE_REGISTER.jsonl", "evidence_id")):
            for line_number, line in enumerate((EXTERNAL_SOURCE / name).read_text(encoding="utf-8-sig").splitlines(), 1):
                value = json.loads(line)
                identifier = value.get(key)
                if identifier in source_ids:
                    selected_register_rows.append({
                        "identifier": identifier,
                        "source_file": name,
                        "source_line": line_number,
                        "source_row": value,
                    })
                    resolved_ids.add(identifier)
        if resolved_ids != source_ids:
            raise ValueError(f"planning authority snapshot has unresolved references: {sorted(source_ids - resolved_ids)}")
        snapshot = {
            "recorded_at": RECORDED_AT,
            "schema_id": f"{SCHEMA_ID}/authority-snapshot",
            "selected_register_rows": sorted(selected_register_rows, key=lambda row: row["identifier"]),
            "source_file_facts": [
                {"bytes": expected_bytes, "name": name, "sha256": expected_sha}
                for name, (expected_bytes, expected_sha) in sorted(EXPECTED.items())
            ],
            "tables": tables,
        }
        OUT.mkdir(parents=True, exist_ok=True)
        write_json(AUTHORITY_SNAPSHOT, snapshot)
    if not AUTHORITY_SNAPSHOT.is_file():
        raise ValueError("repo-local educational-access authority snapshot is absent")
    snapshot = json.loads(AUTHORITY_SNAPSHOT.read_text(encoding="utf-8"))
    expected_facts = [
        {"bytes": expected_bytes, "name": name, "sha256": expected_sha}
        for name, (expected_bytes, expected_sha) in sorted(EXPECTED.items())
    ]
    if snapshot.get("schema_id") != f"{SCHEMA_ID}/authority-snapshot" or snapshot.get("source_file_facts") != expected_facts:
        raise ValueError("repo-local educational-access authority snapshot identity changed")
    if set(snapshot.get("tables", {})) != set(table_names):
        raise ValueError("repo-local educational-access authority table closure changed")
    return snapshot


def integer(value: str) -> int | None:
    return int(value) if value.strip() else None


def number(value: str) -> float | None:
    return float(value) if value.strip() else None


def refs(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def artifact(path: Path, role: str) -> dict[str, Any]:
    return {
        "bytes": path.stat().st_size,
        "path": path.relative_to(OUT).as_posix(),
        "role": role,
        "sha256": sha256_path(path),
    }


def build() -> dict[str, Any]:
    snapshot = build_or_load_authority_snapshot()
    tables = snapshot["tables"]

    curriculum_units = []
    for row in tables["curriculum_units.csv"]:
        curriculum_units.append({
            "accessibility_formats": [item.strip() for item in row["accessibility_formats"].split(" and ") if item.strip()],
            "curriculum_unit_id": row["curriculum_unit_id"],
            "domain": row["domain"],
            "estimated_source_tokens": integer(row["estimated_source_tokens"]),
            "level": row["level"],
            "license": row["license"],
            "notes": row["notes"],
            "prerequisites": [item.strip() for item in row["prerequisites"].split(";") if item.strip()],
            "record_type": "planning_curriculum_unit",
            "schema_id": SCHEMA_ID,
            "source_format": row["source_format"],
            "source_ids": refs(row["source_id"]),
            "source_project": row["source_project"],
            "unit_title": row["unit_title"],
            "work_title": row["work_title"],
        })

    portfolios = []
    relations = []
    for row in tables["curriculum_portfolios.csv"]:
        portfolios.append({
            "cumulative_result": row["cumulative_result"],
            "exact_content": row["exact_content"],
            "notes": row["notes"],
            "portfolio_id": row["portfolio_id"],
            "portfolio_name": row["portfolio_name"],
            "preferred_depth_expression": row["preferred_depth"],
            "prerequisite_portfolio": row["prerequisite_portfolio"] or None,
            "raw_units": integer(row["raw_units"]),
            "record_type": "planning_curriculum_portfolio",
            "schema_id": SCHEMA_ID,
            "source_alpha_tokens": integer(row["source_alpha_tokens"]),
            "source_ids": refs(row["source_ids"]),
            "source_project": row["source_project"],
        })
        if row["prerequisite_portfolio"]:
            relations.append({
                "from_id": row["portfolio_id"],
                "record_type": "planning_relation",
                "relation_type": "requires_portfolio",
                "schema_id": SCHEMA_ID,
                "to_id": row["prerequisite_portfolio"],
            })

    depths = []
    for row in tables["adaptation_depths.csv"]:
        depths.append({
            "depth_id": row["depth_id"],
            "educational_status": row["educational_status"],
            "included_components": row["included_components"],
            "name": row["name"],
            "notes": row["notes"],
            "record_type": "adaptation_depth",
            "schema_id": SCHEMA_ID,
            "workload_multiplier": {"base": number(row["workload_multiplier_base"]), "high": number(row["workload_multiplier_high"]), "low": number(row["workload_multiplier_low"])},
        })

    derivatives = []
    for row in tables["accessibility_derivatives.csv"]:
        derivatives.append({
            "access_gain_axis": row["access_gain_axis"],
            "derivative_id": row["derivative_id"],
            "name": row["name"],
            "notes": row["notes"],
            "record_type": "accessibility_derivative",
            "schema_id": SCHEMA_ID,
            "scope": row["scope"],
            "workload_increment": {"base": number(row["workload_increment_base"]), "high": number(row["workload_increment_high"]), "low": number(row["workload_increment_low"])},
        })

    assumptions = [{
        "empirical_status": row["empirical_status"],
        "high": row["high"],
        "base": row["base"],
        "low": row["low"],
        "notes": row["notes"],
        "parameter": row["parameter"],
        "record_type": "compute_assumption",
        "schema_id": SCHEMA_ID,
        "unit": row["unit"],
    } for row in tables["compute_assumptions.csv"]]

    scenario_integer_fields = {
        "source_alpha_tokens", "editable_units", "uncached_input_tokens", "cached_input_tokens", "output_tokens", "gross_tokens"
    }
    scenario_float_fields = {
        "api_equivalent_usd", "initial_translation_usd", "critique_correction_usd", "build_qa_usd", "retry_allowance_usd", "older_denominator_usd", "no_cache_usd"
    }
    scenarios = []
    for row in tables["compute_scenarios.csv"]:
        value: dict[str, Any] = {"record_type": "compute_scenario", "schema_id": SCHEMA_ID}
        for key, item in row.items():
            value[key] = integer(item) if key in scenario_integer_fields else number(item) if key in scenario_float_fields else refs(item) if key == "source_ids" else item
        value["gross_reconciliation_delta_tokens"] = value["gross_tokens"] - (
            value["uncached_input_tokens"] + value["cached_input_tokens"] + value["output_tokens"]
        )
        scenarios.append(value)

    model_contract = {
        "cardinal_unit": "one exact linguistic intervention against FR-2/D3",
        "compute_denominator": "gross_tokens = uncached_input_tokens + cached_input_tokens + output_tokens",
        "fixed_comparator": {"adaptation_depth": "D3", "curriculum_portfolio": "FR-2", "source_alpha_tokens": 120083, "units": 210},
        "implemented_score_views": ["gross", "conservative", "base", "optimistic", "scarcity"],
        "population_overlap_policy": "non-overlapping cells by language variety, territory, script/orthography, learner stratum, and reference year",
        "record_type": "educational_access_model_contract",
        "schema_id": SCHEMA_ID,
        "selection_lane_order": ["base", "optimistic", "scarcity"],
        "unimplemented_must_not_be_implied": ["Monte Carlo uncertainty", "equity/prestige objective weights", "learning-effect adjustment", "empirical reuse calibration"],
    }

    OUT.mkdir(parents=True, exist_ok=True)
    outputs = {
        "curriculum_units.jsonl": (curriculum_units, "planning_curriculum_units"),
        "curriculum_portfolios.jsonl": (portfolios, "planning_curriculum_portfolios"),
        "portfolio_relations.jsonl": (sorted(relations, key=lambda row: (row["from_id"], row["to_id"])), "planning_portfolio_relations"),
        "adaptation_depths.jsonl": (depths, "planning_adaptation_depths"),
        "accessibility_derivatives.jsonl": (derivatives, "planning_accessibility_derivatives"),
        "compute_assumptions.jsonl": (assumptions, "planning_compute_assumptions"),
        "compute_scenarios.jsonl": (scenarios, "planning_compute_scenarios"),
    }
    files = []
    for name, (rows, role) in outputs.items():
        write_jsonl(OUT / name, rows)
        files.append(artifact(OUT / name, role))
    write_json(OUT / "model_contract.json", model_contract)
    files.append(artifact(OUT / "model_contract.json", "planning_model_contract"))

    manifest = {
        "dataset_id": "planning:educational-access:v2.1:0.1.0",
        "files": sorted(files, key=lambda row: row["path"]),
        "input_authority": [{
            "bytes": AUTHORITY_SNAPSHOT.stat().st_size,
            "locator": AUTHORITY_SNAPSHOT.relative_to(ROOT).as_posix(),
            "locator_base": "repository_root",
            "role": "minimal_repo_local_derived_planning_authority",
            "sha256": sha256_path(AUTHORITY_SNAPSHOT),
            "upstream_source_file_facts": snapshot["source_file_facts"],
        }],
        "limitations": [
            "Planning estimates are source-versioned scenarios, not observed account usage or measured learning effects.",
            "The package models curriculum selection, translation depth, accessibility derivatives, and compute; it does not change canonical course ownership.",
            "Population and language-ranking tables remain in the research dossier and are not copied into the public curriculum backend.",
            "The repo-local authority snapshot contains the six used planning tables and only the ten register rows they reference; it preserves upstream file/line/hash provenance without copying unrelated research records.",
            "The strict federation-unit v2.1 schemas describe course records; this planning package uses its separately identified additive contract.",
        ],
        "record_counts": {
            "accessibility_derivatives": len(derivatives),
            "adaptation_depths": len(depths),
            "compute_assumptions": len(assumptions),
            "compute_scenarios": len(scenarios),
            "curriculum_portfolios": len(portfolios),
            "curriculum_units": len(curriculum_units),
            "model_contracts": 1,
            "portfolio_relations": len(relations),
        },
        "recorded_at": RECORDED_AT,
        "schema_id": SCHEMA_ID,
        "source_mode": "repo_local_minimal_frozen_authority_snapshot",
    }
    write_json(OUT / "manifest.json", manifest)
    return manifest


if __name__ == "__main__":
    built = build()
    print(canonical({"dataset_id": built["dataset_id"], "record_counts": built["record_counts"], "result": "pass"}))
