#!/usr/bin/env python3
"""Independently validate the v2.1 educational-access planning package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "backend/v2.1/planning/educational-access"
AUTHORITY_SNAPSHOT = PACKAGE / "authority_snapshot.json"
SCHEMA_ID = "interlanguage/global-backend-v2.1-educational-access-planning/0.1.0"
EXPECTED_COUNTS = {
    "accessibility_derivatives": 8,
    "adaptation_depths": 5,
    "compute_assumptions": 12,
    "compute_scenarios": 3,
    "curriculum_portfolios": 13,
    "curriculum_units": 29,
    "model_contracts": 1,
    "portfolio_relations": 10,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        value = json.loads(line)
        if not isinstance(value, dict) or canonical(value) != line:
            raise ValueError(f"{path.name}:{number}: noncanonical JSON object")
        if value.get("schema_id") != SCHEMA_ID:
            raise ValueError(f"{path.name}:{number}: schema mismatch")
        rows.append(value)
    return rows


def unique(rows: list[dict[str, Any]], key: str) -> set[str]:
    values = [row.get(key) for row in rows]
    if any(not isinstance(value, str) or not value for value in values) or len(values) != len(set(values)):
        raise ValueError(f"{key} identity is missing or duplicated")
    return set(values)


def main() -> None:
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_id") != SCHEMA_ID or manifest.get("source_mode") != "repo_local_minimal_frozen_authority_snapshot":
        raise ValueError("planning manifest identity/mode mismatch")
    if manifest.get("record_counts") != EXPECTED_COUNTS:
        raise ValueError("planning record counts changed")
    declared = {row["path"]: row for row in manifest["files"]}
    actual = {path.relative_to(PACKAGE).as_posix() for path in PACKAGE.iterdir() if path.is_file()} - {"README.md", "manifest.json", "validation_report.json", "authority_snapshot.json"}
    if set(declared) != actual:
        raise ValueError(f"planning inventory mismatch: declared={sorted(declared)}, actual={sorted(actual)}")
    for name, fact in declared.items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"unsafe planning path: {name}")
        path = PACKAGE.joinpath(*relative.parts)
        if (path.stat().st_size, sha256(path)) != (fact["bytes"], fact["sha256"]):
            raise ValueError(f"planning file identity mismatch: {name}")
    authority_facts = manifest.get("input_authority")
    if not isinstance(authority_facts, list) or len(authority_facts) != 1:
        raise ValueError("planning package must bind exactly one minimal repo-local authority snapshot")
    authority_fact = authority_facts[0]
    if authority_fact.get("locator_base") != "repository_root" or authority_fact.get("locator") != "backend/v2.1/planning/educational-access/authority_snapshot.json":
        raise ValueError("planning authority locator is not the repo-local frozen snapshot")
    if (AUTHORITY_SNAPSHOT.stat().st_size, sha256(AUTHORITY_SNAPSHOT)) != (authority_fact["bytes"], authority_fact["sha256"]):
        raise ValueError("planning repo-local authority snapshot identity mismatch")
    snapshot = json.loads(AUTHORITY_SNAPSHOT.read_text(encoding="utf-8"))
    if snapshot.get("schema_id") != f"{SCHEMA_ID}/authority-snapshot" or len(snapshot.get("selected_register_rows", [])) != 10:
        raise ValueError("planning minimal authority snapshot schema/register closure mismatch")

    units = load_jsonl(PACKAGE / "curriculum_units.jsonl")
    portfolios = load_jsonl(PACKAGE / "curriculum_portfolios.jsonl")
    relations = load_jsonl(PACKAGE / "portfolio_relations.jsonl")
    depths = load_jsonl(PACKAGE / "adaptation_depths.jsonl")
    derivatives = load_jsonl(PACKAGE / "accessibility_derivatives.jsonl")
    assumptions = load_jsonl(PACKAGE / "compute_assumptions.jsonl")
    scenarios = load_jsonl(PACKAGE / "compute_scenarios.jsonl")
    unit_ids = unique(units, "curriculum_unit_id")
    portfolio_ids = unique(portfolios, "portfolio_id")
    depth_ids = unique(depths, "depth_id")
    derivative_ids = unique(derivatives, "derivative_id")
    unique(assumptions, "parameter")
    unique(scenarios, "scenario")
    if len(unit_ids) != 29 or len(portfolio_ids) != 13 or depth_ids != {"D0", "D1", "D2", "D3", "D4"} or len(derivative_ids) != 8:
        raise ValueError("planning identity closure changed")

    expected_relations = {
        (row["portfolio_id"], row["prerequisite_portfolio"])
        for row in portfolios if row["prerequisite_portfolio"]
    }
    actual_relations = {(row["from_id"], row["to_id"]) for row in relations}
    if actual_relations != expected_relations or any(left not in portfolio_ids or right not in portfolio_ids for left, right in actual_relations):
        raise ValueError("portfolio prerequisite graph mismatch")
    visiting: set[str] = set()
    visited: set[str] = set()
    prerequisites = {left: right for left, right in actual_relations}
    def visit(node: str) -> None:
        if node in visiting:
            raise ValueError(f"portfolio cycle at {node}")
        if node in visited:
            return
        visiting.add(node)
        if node in prerequisites:
            visit(prerequisites[node])
        visiting.remove(node)
        visited.add(node)
    for node in portfolio_ids:
        visit(node)

    for row in depths:
        values = row["workload_multiplier"]
        if not (0 <= values["low"] <= values["base"] <= values["high"]):
            raise ValueError(f"adaptation-depth workload interval invalid: {row['depth_id']}")
    for row in derivatives:
        values = row["workload_increment"]
        if not (0 <= values["low"] <= values["base"] <= values["high"]):
            raise ValueError(f"accessibility workload interval invalid: {row['derivative_id']}")
    for row in scenarios:
        delta = row["gross_tokens"] - (row["uncached_input_tokens"] + row["cached_input_tokens"] + row["output_tokens"])
        if row.get("gross_reconciliation_delta_tokens") != delta or abs(delta) > 1000:
            raise ValueError(f"gross-token reconciliation/rounding bound failed: {row['scenario']}")
        component_cost = row["initial_translation_usd"] + row["critique_correction_usd"] + row["build_qa_usd"] + row["retry_allowance_usd"]
        if abs(component_cost - row["api_equivalent_usd"]) > 0.011:
            raise ValueError(f"cost-component reconciliation failed: {row['scenario']}")

    source_ids = {
        source_id
        for row in [*units, *portfolios, *scenarios]
        for source_id in row.get("source_ids", [])
    }
    register_ids = {
        row.get("identifier")
        for row in snapshot["selected_register_rows"]
        if isinstance(row, dict) and isinstance(row.get("identifier"), str)
    }
    missing_refs = sorted(source_ids - register_ids)
    if missing_refs:
        raise ValueError(f"planning source references unresolved: {missing_refs}")

    contract = json.loads((PACKAGE / "model_contract.json").read_text(encoding="utf-8"))
    if contract.get("fixed_comparator") != {"adaptation_depth": "D3", "curriculum_portfolio": "FR-2", "source_alpha_tokens": 120083, "units": 210}:
        raise ValueError("educational-access fixed comparator changed")
    report = {
        "dataset_id": manifest["dataset_id"],
        "file_count": len(declared),
        "record_counts": EXPECTED_COUNTS,
        "resolved_source_reference_count": len(source_ids),
        "result": "pass",
    }
    (PACKAGE / "validation_report.json").write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(canonical(report))


if __name__ == "__main__":
    main()
