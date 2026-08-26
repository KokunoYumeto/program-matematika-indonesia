#!/usr/bin/env python3
"""Validate the educational-access federation, projections, and public catalog."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import uuid
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


REPO = Path(__file__).resolve().parents[1]
WORKSPACE = REPO.parents[2]
PACKAGE = REPO / "backend/research/educational-access-v0.1.0"
PUBLIC = REPO / "docs/data/educational-access.json"
SCHEMA = REPO / "schemas/educational-access-federation-v1.schema.json"
NAMESPACE = uuid.UUID("7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd")
RECORDED_AT = "2026-08-25T00:40:00+02:00"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-live-source-replay",
        action="store_true",
        help="Fail if the mutable workspace paths no longer equal this frozen package's source facts.",
    )
    args = parser.parse_args()
    errors: list[str] = []
    package = json.loads((PACKAGE / "federation.json").read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(package), key=lambda item: list(item.path)):
        errors.append(f"schema:{'/'.join(map(str, error.path))}:{error.message}")

    package_schema = PACKAGE / "schema/educational-access-federation-v1.schema.json"
    if package_schema.read_bytes() != SCHEMA.read_bytes():
        errors.append("package schema is not byte-identical to repository schema")

    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    listed = {item["path"]: item for item in manifest["files"]}
    physical = {
        path.relative_to(PACKAGE).as_posix(): path
        for path in PACKAGE.rglob("*")
        if path.is_file() and path.name not in {"README.md", "manifest.json", "validation_report.json"}
    }
    if set(listed) != set(physical):
        errors.append(f"manifest inventory mismatch missing={sorted(set(physical)-set(listed))} extra={sorted(set(listed)-set(physical))}")
    for rel, path in physical.items():
        fact = listed[rel]
        if path.stat().st_size != fact["bytes"] or sha(path) != fact["sha256"]:
            errors.append(f"manifest byte/hash mismatch:{rel}")

    table_names = set(package["tables"])
    ids: dict[str, str] = {}
    stable_pairs: set[tuple[str, str]] = set()
    all_records: list[dict[str, Any]] = []
    for table, rows in package["tables"].items():
        jsonl_path = PACKAGE / "data" / f"{table}.jsonl"
        jsonl_rows = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines() if line]
        if jsonl_rows != rows:
            errors.append(f"JSONL projection mismatch:{table}")
        csv_path = PACKAGE / "csv" / f"{table}.csv"
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            csv_rows = list(csv.DictReader(handle))
        if len(csv_rows) != len(rows):
            errors.append(f"CSV row count mismatch:{table}")
        else:
            for index, (csv_row, row) in enumerate(zip(csv_rows, rows), 1):
                try:
                    rebuilt = json.loads(csv_row["record_json"])
                except Exception as exc:  # pragma: no cover - fail-closed path
                    errors.append(f"CSV record_json parse failure:{table}:{index}:{exc}")
                    continue
                if rebuilt != row:
                    errors.append(f"CSV round-trip mismatch:{table}:{index}")
        for row in rows:
            expected = f"urn:uuid:{uuid.uuid5(NAMESPACE, row['record_type'] + ':' + row['stable_key'])}"
            if row["id"] != expected:
                errors.append(f"UUIDv5 mismatch:{row['record_type']}:{row['stable_key']}")
            if row["id"] in ids:
                errors.append(f"duplicate id:{row['id']}")
            ids[row["id"]] = table
            pair = (row["record_type"], row["stable_key"])
            if pair in stable_pairs:
                errors.append(f"duplicate stable key:{pair}")
            stable_pairs.add(pair)
            all_records.append(row)

    statuses = {item["table_name"]: item for item in package["table_statuses"]}
    for table in table_names:
        status = statuses.get(table)
        if not status or not status["materialized"] or status["record_count"] != len(package["tables"][table]):
            errors.append(f"materialized table status mismatch:{table}")
    for table, status in statuses.items():
        if not status["materialized"] and (table in table_names or status["record_count"] != 0):
            errors.append(f"unmaterialized table emitted or nonzero:{table}")

    source_fact_mismatches: list[str] = []
    for fact in package["source_facts"]:
        source = WORKSPACE / Path(fact["path"])
        if not source.is_file():
            source_fact_mismatches.append(f"source fact missing:{fact['path']}")
        elif source.stat().st_size != fact["bytes"] or sha(source) != fact["sha256"]:
            source_fact_mismatches.append(f"source fact mismatch:{fact['path']}")
    if args.require_live_source_replay:
        errors.extend(source_fact_mismatches)

    project_keys = {row["payload"]["project_key"] for row in package["tables"]["research_projects"]}
    for row in package["tables"]["research_workstreams"]:
        if row["payload"]["project_key"] not in project_keys:
            errors.append(f"workstream project FK missing:{row['stable_key']}")
    profile_ids = {row["id"] for row in package["tables"]["language_profiles"]}
    profile_keys = {row["payload"]["profile_id"] for row in package["tables"]["language_profiles"]}
    for row in package["tables"]["recommendations"]:
        payload = row["payload"]
        if payload["profile_record_id"] is not None and payload["profile_record_id"] not in profile_ids:
            errors.append(f"recommendation profile FK missing:{row['stable_key']}")
        if payload["profile_record_id"] is not None and payload["profile_id"] not in profile_keys:
            errors.append(f"recommendation profile key missing:{row['stable_key']}")

    evidence_ids = {row["payload"]["evidence_id"] for row in package["tables"]["evidence_sources"]}
    for table in ["language_profiles", "recommendations", "bridge_surfaces", "accessibility_interventions"]:
        for row in package["tables"][table]:
            for evidence_id in row["payload"].get("evidence_ids", []):
                if evidence_id not in evidence_ids:
                    errors.append(f"evidence FK missing:{table}:{row['stable_key']}:{evidence_id}")

    asset_ids = {row["payload"]["asset_id"] for row in package["tables"]["asset_sources"]}
    for table in ["language_profiles", "recommendations", "bridge_surfaces", "accessibility_interventions", "manager_coverage"]:
        for row in package["tables"][table]:
            for asset_id in row["payload"].get("asset_ids", []):
                if asset_id not in asset_ids:
                    errors.append(f"asset FK missing:{table}:{row['stable_key']}:{asset_id}")

    course_keys = {row["payload"]["course_key"] for row in package["tables"]["curriculum_resources"]}
    if len(course_keys) != 40:
        errors.append(f"curriculum resource count/identity mismatch:{len(course_keys)}")
    for row in package["tables"]["curriculum_resources"]:
        for prerequisite in row["payload"]["prerequisite_course_keys"]:
            if prerequisite not in course_keys:
                errors.append(f"curriculum prerequisite missing:{row['stable_key']}:{prerequisite}")

    records_jsonl = [json.loads(line) for line in (PACKAGE / "records.jsonl").read_text(encoding="utf-8").splitlines() if line]
    expected_all = sorted(all_records, key=lambda item: (item["record_type"], item["stable_key"]))
    if records_jsonl != expected_all:
        errors.append("aggregate records.jsonl mismatch")
    with (PACKAGE / "records.csv").open("r", encoding="utf-8", newline="") as handle:
        aggregate_csv = list(csv.DictReader(handle))
    if len(aggregate_csv) != len(expected_all):
        errors.append("aggregate records.csv count mismatch")
    elif any(json.loads(csv_row["record_json"]) != row for csv_row, row in zip(aggregate_csv, expected_all)):
        errors.append("aggregate records.csv round-trip mismatch")

    public = json.loads(PUBLIC.read_text(encoding="utf-8"))
    public_copy = json.loads((PACKAGE / "public-catalog.json").read_text(encoding="utf-8"))
    if public != public_copy:
        errors.append("public catalog copy mismatch")
    expected_public_counts = {
        "researchProjects": len(package["tables"]["research_projects"]),
        "workstreams": len(package["tables"]["research_workstreams"]),
        "profiles": len(package["tables"]["language_profiles"]),
        "recommendations": len(package["tables"]["recommendations"]),
        "bridges": len(package["tables"]["bridge_surfaces"]),
        "accessibility": len(package["tables"]["accessibility_interventions"]),
        "curriculum": len(package["tables"]["curriculum_resources"]),
    }
    for key, count in expected_public_counts.items():
        if len(public[key]) != count:
            errors.append(f"public catalog count mismatch:{key}")
    if not any(item["research_state"] == "active_unmaterialized" for item in public["workstreams"]):
        errors.append("active unfinished workstreams are not explicit")
    if public["method"]["rankingBoundary"].find("not yet populated") < 0:
        errors.append("ranking incompleteness boundary missing")

    report = {
        "schema_id": "interlanguage/educational-access-federation-validation/v1",
        "recorded_at": RECORDED_AT,
        "result": "pass" if not errors else "fail",
        "schema_validation": "pass" if not any(item.startswith("schema:") for item in errors) else "fail",
        "records": len(all_records),
        "table_counts": {table: len(rows) for table, rows in package["tables"].items()},
        "materialized_tables": len(package["tables"]),
        "declared_unmaterialized_tables": len([item for item in package["table_statuses"] if not item["materialized"]]),
        "manifest_files": len(manifest["files"]),
        "uuidv5_and_stable_key_check": "pass" if not any("UUIDv5" in item or "stable key" in item or "duplicate id" in item for item in errors) else "fail",
        "projection_round_trip": "pass" if not any("projection" in item or "round-trip" in item for item in errors) else "fail",
        "source_fact_replay": "pass_current_live" if not source_fact_mismatches else "frozen_source_facts_retained_live_workspace_diverged",
        "source_fact_live_mismatches": source_fact_mismatches,
        "strict_live_source_replay_required": args.require_live_source_replay,
        "foreign_key_checks": "pass" if not any("FK missing" in item or "prerequisite missing" in item for item in errors) else "fail",
        "public_catalog_check": "pass" if not any(item.startswith("public") or "workstreams" in item or "ranking incompleteness" in item for item in errors) else "fail",
        "errors": errors,
    }
    (PACKAGE / "validation_report.json").write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
