#!/usr/bin/env python3
"""Run isolated mutation probes against C80 semantic validation."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from v231_adapter_common import compact_json, read_jsonl, write_json, write_jsonl
from validate_c80_openlogic_v231 import validate_c80_semantics


Mutation = Callable[[Path], None]


def mutate_table(package: Path, table: str, mutate: Callable[[list[dict[str, Any]]], None]) -> None:
    path = package / "tables" / f"{table}.jsonl"
    rows = read_jsonl(path)
    mutate(rows)
    write_jsonl(path, rows)


def mutate_json(package: Path, relative: str, mutate: Callable[[dict[str, Any]], None]) -> None:
    import json
    path = package / relative
    value = json.loads(path.read_text(encoding="utf-8"))
    mutate(value)
    write_json(path, value)


def probes() -> list[tuple[str, Mutation]]:
    def delete_unit(rows: list[dict[str, Any]]) -> None:
        rows.pop()

    def missing_translation(rows: list[dict[str, Any]]) -> None:
        rows[0]["payload"]["translation_state"] = "missing"

    def reader_reach_drift(rows: list[dict[str, Any]]) -> None:
        rows[0]["payload"]["canonical_reader_reachable"] = False

    def delete_relation(rows: list[dict[str, Any]]) -> None:
        rows.pop()

    def invent_html(rows: list[dict[str, Any]]) -> None:
        rows[0]["payload"]["route_kind"] = "semantic_html_unit"
        rows[0]["payload"]["target_kind"] = "readable_html"

    def invent_anchor(rows: list[dict[str, Any]]) -> None:
        rows[0]["payload"]["unit_id"] = "urn:uuid:00000000-0000-4000-8000-000000000000"
        rows[0]["payload"]["unit_anchor"] = "#unit-1"

    def weaken_rights(rows: list[dict[str, Any]]) -> None:
        rows[0]["payload"]["license_expression"] = "CC-BY-NC-4.0"

    def artifact_hash_drift(rows: list[dict[str, Any]]) -> None:
        rows[0]["payload"]["sha256"] = "0" * 64

    def v1_crosswalk_drift(rows: list[dict[str, Any]]) -> None:
        rows[0]["payload"]["previous_v1_unit_id"] = "urn:uuid:00000000-0000-4000-8000-000000000000"

    def centralize_content(rows: list[dict[str, Any]]) -> None:
        rows[0]["payload"]["content_included_in_adapter"] = True

    def stale_translation(value: dict[str, Any]) -> None:
        value["records"][0]["state"] = "translated_file_present"

    def loose_reader(rows: list[dict[str, Any]]) -> None:
        rows[0]["payload"]["filename"] = "00_OPENLOGIC_id_COMPLETE_READER_OLP-0722.pdf"

    return [
        ("missing_unit", lambda package: mutate_table(package, "units", delete_unit)),
        ("stale_missing_unit_state", lambda package: mutate_table(package, "units", missing_translation)),
        ("reader_reachability_drift", lambda package: mutate_table(package, "units", reader_reach_drift)),
        ("missing_import_relation", lambda package: mutate_table(package, "relations", delete_relation)),
        ("invented_html_route", lambda package: mutate_table(package, "routes", invent_html)),
        ("invented_unit_anchor", lambda package: mutate_table(package, "routes", invent_anchor)),
        ("rights_license_drift", lambda package: mutate_table(package, "rights", weaken_rights)),
        ("public_artifact_hash_drift", lambda package: mutate_table(package, "artifacts", artifact_hash_drift)),
        ("prior_v1_identity_drift", lambda package: mutate_table(package, "units", v1_crosswalk_drift)),
        ("centralized_content_body_flag", lambda package: mutate_table(package, "content_bindings", centralize_content)),
        ("stale_translation_sidecar", lambda package: mutate_json(package, "translation-state-index-v0.2.0.json", stale_translation)),
        ("loose_934_page_reader_drift", lambda package: mutate_table(package, "artifacts", loose_reader)),
    ]


def run(package: Path) -> dict[str, Any]:
    package = package.resolve()
    validate_c80_semantics(package)
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="c80-openlogic-negative-") as temp:
        root = Path(temp)
        for ordinal, (name, mutation) in enumerate(probes(), 1):
            candidate = root / f"probe-{ordinal:02d}"
            shutil.copytree(package, candidate)
            mutation(candidate)
            rejected = False
            error = ""
            try:
                validate_c80_semantics(candidate)
            except Exception as exc:
                rejected = True
                error = f"{type(exc).__name__}: {exc}"
            if not rejected:
                raise RuntimeError(f"negative probe was accepted: {name}")
            results.append({"probe": name, "mutation_rejected": True, "validator_error": error})
            shutil.rmtree(candidate)
    return {
        "schema_id": "program-matematika-indonesia/c80-openlogic-v231-negative-probes/1.0.0",
        "status": "PASS",
        "baseline_semantic_validation": "PASS",
        "probe_count": len(results),
        "all_mutations_rejected": all(row["mutation_rejected"] for row in results),
        "temporary_probe_trees_retained": 0,
        "results": results,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = run(args.package)
        write_json(args.report, report)
        print(compact_json(report))
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
