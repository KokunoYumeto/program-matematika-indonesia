#!/usr/bin/env python3
"""Run isolated generic and semantic mutation probes against a C130 package."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Iterable

from v231_adapter_common import compact_json, read_json, read_jsonl, write_json, write_jsonl
from validate_c130_operations_research_v231 import validate_c130_semantics
from validate_lane_adapter_v231 import validate_package


Mutation = Callable[[Path], None]
Probe = tuple[str, Mutation, tuple[str, ...]]
GENERIC = "generic"
SEMANTIC = "c130_semantic"


def mutate_table(package: Path, table: str, mutate: Callable[[list[dict[str, Any]]], None]) -> None:
    path = package / "tables" / f"{table}.jsonl"
    rows = read_jsonl(path)
    mutate(rows)
    write_jsonl(path, rows)


def mutate_json(package: Path, relative: str, mutate: Callable[[dict[str, Any]], None]) -> None:
    path = package / relative
    value = read_json(path)
    if not isinstance(value, dict):
        raise RuntimeError(f"probe target is not a JSON object: {relative}")
    mutate(value)
    write_json(path, value)


def require_rows(rows: list[dict[str, Any]], label: str) -> None:
    if not rows:
        raise RuntimeError(f"probe requires a non-empty {label} table")


def remove_last(rows: list[dict[str, Any]], label: str) -> None:
    require_rows(rows, label)
    rows.pop()


def remove_segment_binding(rows: list[dict[str, Any]]) -> None:
    require_rows(rows, "native_bindings")
    for ordinal, row in enumerate(rows):
        if "segment" in compact_json(row).lower():
            rows.pop(ordinal)
            return
    raise RuntimeError("probe could not locate a segment native binding")


def drift_first_hash(value: Any, preferred_keys: Iterable[str] = ()) -> None:
    if isinstance(value, dict):
        for key in preferred_keys:
            candidate = value.get(key)
            if isinstance(candidate, str) and len(candidate) == 64:
                value[key] = "0" * 64 if candidate != "0" * 64 else "f" * 64
                return
        for key in sorted(value):
            candidate = value[key]
            if "sha256" in key.lower() and isinstance(candidate, str) and len(candidate) == 64:
                value[key] = "0" * 64 if candidate != "0" * 64 else "f" * 64
                return
        for key in sorted(value):
            try:
                drift_first_hash(value[key], preferred_keys)
                return
            except LookupError:
                pass
    elif isinstance(value, list):
        for item in value:
            try:
                drift_first_hash(item, preferred_keys)
                return
            except LookupError:
                pass
    raise LookupError("no SHA-256 field found in probe target")


def mutate_source_artifact_hash(rows: list[dict[str, Any]]) -> None:
    require_rows(rows, "artifacts")
    for row in rows:
        try:
            drift_first_hash(row["payload"], ("source_sha256", "artifact_sha256", "sha256"))
            return
        except LookupError:
            pass
    raise RuntimeError("probe could not locate an artifact SHA-256 field")


def mutate_rights_license(rows: list[dict[str, Any]]) -> None:
    require_rows(rows, "rights")
    payload = rows[0]["payload"]
    payload["license_expression"] = (
        "CC-BY-NC-4.0" if payload.get("license_expression") != "CC-BY-NC-4.0" else "CC0-1.0"
    )


def mutate_dangling_rights_assignment(rows: list[dict[str, Any]]) -> None:
    require_rows(rows, "rights_assignments")
    rows[0]["payload"]["target_id"] = "urn:uuid:00000000-0000-4000-8000-000000000000"


def mutate_native_html(rows: list[dict[str, Any]]) -> None:
    require_rows(rows, "routes")
    payload = rows[0]["payload"]
    payload["route_kind"] = "semantic_native_html_unit"
    payload["target_kind"] = "learner_readable_html"
    payload["native_html_available"] = True


def mutate_unit_anchor(rows: list[dict[str, Any]]) -> None:
    require_rows(rows, "routes")
    payload = rows[0]["payload"]
    payload["unit_id"] = "urn:uuid:00000000-0000-4000-8000-000000000000"
    payload["unit_anchor"] = "#unit-1"


def mutate_pdf_ua_claim(rows: list[dict[str, Any]]) -> None:
    require_rows(rows, "reader_surfaces")
    payload = rows[0]["payload"]
    payload["pdf_ua_conformance"] = "PDF/UA-1"
    payload["pdf_ua_verified"] = True


def mutate_content_leak(rows: list[dict[str, Any]]) -> None:
    require_rows(rows, "content_bindings")
    payload = rows[0]["payload"]
    payload["content_included_in_adapter"] = True
    payload["prose"] = "invented centralized textbook prose"


def mutate_translation_state(value: dict[str, Any]) -> None:
    records = value.get("records")
    if not isinstance(records, list) or not records or not isinstance(records[0], dict):
        raise RuntimeError("probe requires a non-empty translation-state record list")
    current = records[0].get("state")
    records[0]["state"] = "translated_file_present" if current != "translated_file_present" else "missing"


def mutate_owner_id(rows: list[dict[str, Any]]) -> None:
    require_rows(rows, "native_bindings")
    preferred = ("native_id", "owner_native_id", "native_unit_id", "source_id")
    for row in rows:
        payload = row["payload"]
        for key in preferred:
            value = payload.get(key)
            if isinstance(value, str) and value:
                payload[key] = value + "-drift"
                return
    raise RuntimeError("probe could not locate an owner-native ID field")


def mutate_crosswalk(value: dict[str, Any]) -> None:
    mappings = value.get("mappings")
    if not isinstance(mappings, list) or not mappings or not isinstance(mappings[0], dict):
        raise RuntimeError("probe requires a non-empty namespace mapping list")
    mappings[0]["source_record_id"] = "C130-OWNER-ID-DRIFT"


def mutate_prior_v1_crosswalk(value: dict[str, Any]) -> None:
    mappings = value.get("mappings")
    if not isinstance(mappings, list):
        raise RuntimeError("probe requires namespace mappings")
    for mapping in mappings:
        if mapping.get("source_namespace") == "7790e70a-ae6d-5cf3-b7f5-c53d7d4c0fbd":
            mapping["source_record_id"] = "urn:uuid:00000000-0000-4000-8000-000000000000"
            return
    raise RuntimeError("probe could not locate a prior-v1 namespace mapping")


def mutate_capability(value: dict[str, Any]) -> None:
    capabilities = value.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        raise RuntimeError("probe requires capability declarations")
    row = next(
        (candidate for candidate in capabilities if candidate.get("name") == "publication"),
        capabilities[0],
    )
    row["state"] = "absent" if row.get("state") != "absent" else "materialized"


def mutate_scope(value: dict[str, Any]) -> None:
    roles = value.get("curriculum_role_ids")
    if not isinstance(roles, list) or not roles:
        raise RuntimeError("probe requires a non-empty curriculum role scope")
    value["curriculum_role_ids"] = ["C80"] if roles != ["C80"] else ["C130-STALE"]


def corrupt_csv(package: Path) -> None:
    path = package / "csv" / "units.csv"
    data = path.read_bytes()
    marker = b"stable_id,record_type,canonical_record_json"
    if marker not in data:
        raise RuntimeError("probe could not locate the canonical units CSV header")
    path.write_bytes(data.replace(marker, b"corrupt_id,record_type,canonical_record_json", 1))


def corrupt_manifest(value: dict[str, Any]) -> None:
    build = value.get("build")
    if not isinstance(build, dict) or "build_a_sha256" not in build:
        raise RuntimeError("probe requires a manifest build digest")
    build["build_a_sha256"] = "0" * 64


def corrupt_seal(value: dict[str, Any]) -> None:
    files = value.get("files")
    if not isinstance(files, list) or not files:
        raise RuntimeError("probe requires a non-empty seal inventory")
    files.pop()


def corrupt_checksums(package: Path) -> None:
    path = package / "PACKAGE_CHECKSUMS.sha256"
    rows = path.read_text(encoding="utf-8").splitlines()
    if not rows:
        raise RuntimeError("probe requires a non-empty checksum inventory")
    path.write_text("".join(f"{row}\n" for row in rows[:-1]), encoding="utf-8", newline="\n")


def probes() -> list[Probe]:
    both = (GENERIC, SEMANTIC)
    return [
        ("missing_unit", lambda package: mutate_table(package, "units", lambda rows: remove_last(rows, "units")), both),
        ("missing_segment_binding", lambda package: mutate_table(package, "native_bindings", remove_segment_binding), both),
        ("missing_relation", lambda package: mutate_table(package, "relations", lambda rows: remove_last(rows, "relations")), both),
        ("rights_license_drift", lambda package: mutate_table(package, "rights", mutate_rights_license), both),
        ("dangling_rights_assignment", lambda package: mutate_table(package, "rights_assignments", mutate_dangling_rights_assignment), both),
        ("source_artifact_hash_drift", lambda package: mutate_table(package, "artifacts", mutate_source_artifact_hash), both),
        ("invented_native_html_claim", lambda package: mutate_table(package, "routes", mutate_native_html), both),
        ("invented_unit_anchor", lambda package: mutate_table(package, "routes", mutate_unit_anchor), both),
        ("invented_pdf_ua_claim", lambda package: mutate_table(package, "reader_surfaces", mutate_pdf_ua_claim), both),
        ("centralized_prose_content_leak", lambda package: mutate_table(package, "content_bindings", mutate_content_leak), both),
        ("translation_state_mismatch", lambda package: mutate_json(package, "translation-state-index-v0.2.0.json", mutate_translation_state), both),
        ("csv_projection_corruption", corrupt_csv, (GENERIC,)),
        ("manifest_corruption", lambda package: mutate_json(package, "manifest.json", corrupt_manifest), (GENERIC,)),
        ("seal_inventory_corruption", lambda package: mutate_json(package, "seal.json", corrupt_seal), (GENERIC,)),
        ("checksum_inventory_corruption", corrupt_checksums, (GENERIC,)),
        ("owner_native_id_drift", lambda package: mutate_table(package, "native_bindings", mutate_owner_id), both),
        ("namespace_crosswalk_drift", lambda package: mutate_json(package, "namespace-crosswalk-v0.2.0.json", mutate_crosswalk), both),
        ("prior_v1_namespace_crosswalk_drift", lambda package: mutate_json(package, "namespace-crosswalk-v0.2.0.json", mutate_prior_v1_crosswalk), both),
        ("stale_capability_state", lambda package: mutate_json(package, "capability-declarations-v0.2.0.json", mutate_capability), both),
        ("stale_scope_state", lambda package: mutate_json(package, "scope-declaration-v0.2.0.json", mutate_scope), both),
    ]


def deterministic_error(exc: Exception, replacements: Iterable[tuple[Path | None, str]]) -> str:
    message = f"{type(exc).__name__}: {exc}"
    for path, marker in replacements:
        if path is None:
            continue
        resolved = path.resolve()
        message = message.replace(str(resolved), marker).replace(resolved.as_posix(), marker)
    return message


def invoke_validators(
    package: Path,
    repository_root: Path | None,
    owner_package_root: Path | None,
    require_authorities: bool,
) -> dict[str, dict[str, Any]]:
    replacements = (
        (package, "<package>"),
        (repository_root, "<repository-root>"),
        (owner_package_root, "<owner-package-root>"),
    )
    outcomes: dict[str, dict[str, Any]] = {}
    try:
        validate_package(SimpleNamespace(
            package=package,
            repository_root=repository_root,
            owner_package_root=owner_package_root,
            require_authorities=require_authorities,
            build_a=None,
            build_b=None,
            report=None,
        ))
        outcomes[GENERIC] = {"accepted": True, "error": None}
    except Exception as exc:
        outcomes[GENERIC] = {"accepted": False, "error": deterministic_error(exc, replacements)}

    try:
        validate_c130_semantics(
            package,
            owner_package_root=owner_package_root,
            require_authorities=require_authorities,
        )
        outcomes[SEMANTIC] = {"accepted": True, "error": None}
    except Exception as exc:
        outcomes[SEMANTIC] = {"accepted": False, "error": deterministic_error(exc, replacements)}
    return outcomes


def run(
    package: Path,
    *,
    repository_root: Path | None = None,
    owner_package_root: Path | None = None,
    require_authorities: bool = False,
) -> dict[str, Any]:
    package = package.resolve()
    repository_root = repository_root.resolve() if repository_root is not None else None
    owner_package_root = owner_package_root.resolve() if owner_package_root is not None else None

    baseline = invoke_validators(package, repository_root, owner_package_root, require_authorities)
    failed_baseline = [name for name, outcome in baseline.items() if not outcome["accepted"]]
    if failed_baseline:
        detail = "; ".join(f"{name}: {baseline[name]['error']}" for name in failed_baseline)
        raise RuntimeError(f"baseline validation failed: {detail}")

    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="c130-operations-research-negative-") as temp:
        root = Path(temp)
        for ordinal, (name, mutation, required_rejectors) in enumerate(probes(), 1):
            candidate = root / f"probe-{ordinal:02d}"
            shutil.copytree(package, candidate)
            mutation(candidate)
            outcomes = invoke_validators(candidate, repository_root, owner_package_root, require_authorities)
            missing = [validator for validator in required_rejectors if outcomes[validator]["accepted"]]
            if missing:
                raise RuntimeError(
                    f"negative probe was accepted by required validator(s): {name}: {','.join(missing)}"
                )
            rejected_by = [validator for validator in (GENERIC, SEMANTIC) if not outcomes[validator]["accepted"]]
            if not rejected_by:
                raise RuntimeError(f"negative probe was accepted: {name}")
            results.append({
                "probe": name,
                "mutation_rejected": True,
                "required_rejectors": list(required_rejectors),
                "rejected_by": rejected_by,
                "validators": outcomes,
            })
            shutil.rmtree(candidate)

    return {
        "schema_id": "program-matematika-indonesia/c130-operations-research-v231-negative-probes/1.0.0",
        "status": "PASS",
        "baseline_validation": {GENERIC: "PASS", SEMANTIC: "PASS"},
        "probe_count": len(results),
        "all_mutations_rejected": all(row["mutation_rejected"] for row in results),
        "all_required_rejections_observed": all(
            all(not row["validators"][validator]["accepted"] for validator in row["required_rejectors"])
            for row in results
        ),
        "validators_invoked_per_probe": [GENERIC, SEMANTIC],
        "temporary_probe_trees_retained": 0,
        "results": results,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path)
    parser.add_argument("--owner-package-root", type=Path)
    parser.add_argument("--require-authorities", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = run(
            args.package,
            repository_root=args.repository_root,
            owner_package_root=args.owner_package_root,
            require_authorities=args.require_authorities,
        )
        write_json(args.report, report)
        print(compact_json(report))
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
