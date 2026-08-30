#!/usr/bin/env python3
"""Independently validate the D60 backend-v2.3.1 zero-copy adapter."""

from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable

from v231_adapter_common import (
    AdapterError,
    compact_json,
    identity_set_sha256,
    read_json,
    read_jsonl,
    require,
    sha256_file,
    write_json,
)
from validate_lane_adapter_v231 import validate_package as validate_generic_package


EXPECTED_NATIVE = {
    "artifacts": (279, 254, 233018, "448a222ca2e573b34951cc21ae16ca60db46f06da1f5fec4cc3684bcb1253c29"),
    "assets": (87, 86, 64692, "1df40f8f6ca4f2fbfbe8a7b924a68a153713a20a4eebe1d014d8fb04669945f7"),
    "authority": (6, 6, 4374, "84c622f56dbbd5ba379361245ecfe07bc79c9f4fd6b18ba21b82b5f545211869"),
    "concepts": (535, 535, 169924, "3e55b0612310f5434e6a8e746814504b6b9e9e014dba243dbe8ec2df68614540"),
    "corrections": (566, 564, 599471, "ab6e1a70be761135dfbc3076968c01978894c10520b50ef604004bd1dcea2871"),
    "qa": (230, 214, 129064, "f94f32bf2f652ea704c7abf72ea4df28a8aa3dea31a5f30078e5a074ab99e3c5"),
    "relations": (1443, 1335, 664996, "ac1c2766a8f2179ab210bdbbc425f5ad3ac54f20357259bdddebee0af611d361"),
    "rights": (114, 96, 112823, "8c2fb365a890626d7696056d622548a77f710885ef5053ee72928cf5df9cb5cd"),
    "segments": (2250, 2174, 3740661, "648f35e19b6b42ada3e9b0019b3e482c212a847b5d720c4d663f6ccff23aac78"),
    "terms": (548, 528, 369736, "7ed9ad84065ab452aa63f47dde5606ae0814943a4346ac5fe3499df8403ef50e"),
    "units": (2280, 2204, 3951284, "f3bb94c660780116a29e1089b27b10a60e18034c0ed0d6ce5452d8799a2a8945"),
}

EXPECTED_TABLE_COUNTS = {
    "owner_authorities": 1,
    "datasets": 1,
    "editions": 3,
    "units": 2204,
    "course_unit_memberships": 2204,
    "native_bindings": 6279,
    "content_bindings": 2174,
    "relations": 1337,
    "rights": 96,
    "rights_assignments": 4378,
    "artifacts": 258,
    "build_recipes": 2,
    "reader_surfaces": 2,
    "routes": 2,
    "search_documents": 2204,
    "adapter_profiles": 1,
    "adapter_runs": 1,
    "qa_events": 216,
    "identity_crosswalks": 6279,
}


def current_heads(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = list(rows)
    superseded = {str(row["supersedes"]) for row in rows if row.get("supersedes")}
    return [row for row in rows if str(row["id"]) not in superseded]


def branch_parents(rows: Iterable[dict[str, Any]]) -> list[str]:
    children = collections.Counter(str(row["supersedes"]) for row in rows if row.get("supersedes"))
    return sorted(parent for parent, count in children.items() if count > 1)


def load_tables(package: Path) -> dict[str, list[dict[str, Any]]]:
    return {
        name: read_jsonl(path)
        for path in sorted((package / "tables").glob("*.jsonl"))
        for name in [path.stem]
    }


def recursively_forbidden_prose_keys(value: Any, location: str = "$") -> list[str]:
    failures: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"body", "body_text", "textbook_prose", "source_prose", "target_prose", "note"}:
                failures.append(f"{location}.{key}")
            failures.extend(recursively_forbidden_prose_keys(child, f"{location}.{key}"))
    elif isinstance(value, list):
        for ordinal, child in enumerate(value):
            failures.extend(recursively_forbidden_prose_keys(child, f"{location}[{ordinal}]"))
    return failures


def validate_specific(args: argparse.Namespace) -> dict[str, Any]:
    package = args.package.resolve()
    repository_root = args.repository_root.resolve()
    owner_root = args.owner_package_root.resolve()
    generic_args = SimpleNamespace(
        package=package,
        repository_root=repository_root,
        owner_package_root=owner_root,
        require_authorities=True,
        build_a=args.build_a,
        build_b=args.build_b,
    )
    generic = validate_generic_package(generic_args)
    require(generic["status"] == "PASS", "generic v2.3.1 validation did not pass")
    require(generic["extension_version"] == "0.1.0", "unexpected D60 extension version")
    require(generic["sidecars"]["scope_roles"] == ["D60"], "adapter scope is not exactly D60")

    input_authorities = read_json(package / "INPUT_AUTHORITIES.json")
    closure = input_authorities["owner_native_closure"]
    require(closure["files"] == 11 and closure["records"] == 8338 and closure["bytes"] == 10040043, "input native closure drift")
    require(closure["bundle_sha256"] == "8a3ffc9618e56dfce048c41e938aabef4ffbfd3db20a03a4f52f218985230dbb", "input native bundle digest drift")
    require(closure["materialized_current_native_records"] == 6279, "materialized native closure drift")
    require(input_authorities["owner_native_non_mutation"] is True and input_authorities["body_prose_copied"] is False, "zero-copy input claim drift")

    native: dict[str, list[dict[str, Any]]] = {}
    native_heads: dict[str, list[dict[str, Any]]] = {}
    all_native_ids: set[str] = set()
    for name, (records, heads, byte_count, digest) in EXPECTED_NATIVE.items():
        path = owner_root / "backend" / f"{name}.jsonl"
        require(path.stat().st_size == byte_count and sha256_file(path) == digest, f"owner-native drift: {name}")
        rows = read_jsonl(path)
        require(len(rows) == records, f"owner-native record drift: {name}")
        current = current_heads(rows)
        require(len(current) == heads, f"owner-native head drift: {name}")
        native[name] = rows
        native_heads[name] = current
        for row in rows:
            require(row["id"] not in all_native_ids, f"duplicate global native ID: {row['id']}")
            all_native_ids.add(str(row["id"]))
    require(len(all_native_ids) == 8338, "global native ID census drift")
    require(closure["global_native_id_set_sha256"] == identity_set_sha256(all_native_ids), "global native identity-set drift")

    relation_ids = {str(row["id"]) for rows in native.values() for row in rows}
    require(sum((str(row["from_id"]) in relation_ids) + (str(row["to_id"]) in relation_ids) for row in native["relations"]) == 2886, "native relation endpoint closure drift")

    term_missing_envelope = sum(1 for row in native["terms"] if not row.get("schema") or not row.get("schema_version"))
    current_term_missing_status = sum(1 for row in native_heads["terms"] if not row.get("terminology_status"))
    require(term_missing_envelope == 30, "native malformed-term census drift")
    require(current_term_missing_status == 104, "native terminology-status gap census drift")
    require(branch_parents(native["artifacts"]) == ["artifact:o012-u020-qa"], "artifact branch census drift")
    require(branch_parents(native["corrections"]) == ["correction:o012-u020-adv-0287"], "correction branch census drift")

    tables = load_tables(package)
    observed_counts = {name: len(rows) for name, rows in tables.items()}
    require(observed_counts == EXPECTED_TABLE_COUNTS, f"D60 canonical table census drift: {observed_counts}")
    require(sum(observed_counts.values()) == 27642, "D60 canonical record aggregate drift")

    native_binding_ids = [str(row["payload"]["native_id"]) for row in tables["native_bindings"]]
    require(len(native_binding_ids) == len(set(native_binding_ids)) == 6279, "native binding bijection failure")
    crosswalk_sources = [str(row["payload"]["source_id"]) for row in tables["identity_crosswalks"]]
    require(set(crosswalk_sources) == set(native_binding_ids), "canonical identity crosswalk differs from native bindings")
    sidecar_crosswalk = read_json(package / "namespace-crosswalk-v0.2.0.json")
    owner_mappings = [row for row in sidecar_crosswalk["mappings"] if row["source_namespace"] == "curriculum.interop/o012-d60/0.1.0" and row["source_record_id"] != "course:o012-d60"]
    require(len(owner_mappings) == 6279, "namespace owner mapping count drift")
    require({row["source_record_id"] for row in owner_mappings} == set(native_binding_ids), "namespace owner mapping identity drift")
    require(len(sidecar_crosswalk["mappings"]) == 6281, "namespace total mapping count drift")

    translation = read_json(package / "translation-state-index-v0.2.0.json")
    require(translation["coverage"] == {
        "course_id": "D60",
        "granularity": "current_owner_semantic_unit_head",
        "authority_rows": 2204,
        "indexed_rows": 2204,
        "inferred_rows": 0,
    }, "D60 translation coverage drift")
    require(len(translation["records"]) == 2204 and translation["no_inference"] is True, "D60 translation index drift")
    require(sum(1 for row in translation["records"] if row["source_locator"] is None) == 30, "D60 reader-root source-locator census drift")

    limitation = read_json(package / "evidence" / "D60_NATIVE_LIMITATIONS.json")
    require(limitation["term_rows_missing_schema_or_version"] == 30, "declared term-envelope gap drift")
    require(limitation["current_term_heads_missing_terminology_status"] == 104, "declared terminology gap drift")
    require(limitation["supersession_branch_parents"] == ["artifact:o012-u020-qa", "correction:o012-u020-adv-0287"], "declared branch gap drift")
    require(limitation["unit_anchor_coverage"] == 0 and limitation["pdf_tagged"] is False, "declared learner/accessibility gap drift")
    physical = limitation["artifact_physical_states"]
    require(physical.get("local_hash_match") == 252 and physical.get("declared_path_missing") == 1 and physical.get("declared_identity_stale") == 1, f"artifact physical-state census drift: {physical}")

    html_surfaces = [row for row in tables["reader_surfaces"] if row["payload"].get("format") == "semantic_html"]
    require(len(html_surfaces) == 1, "semantic HTML learner surface census drift")
    html = html_surfaces[0]["payload"]
    require(html["primary"] is True and html["unit_anchor_coverage"] == 0, "HTML learner route overclaim")
    html_url = "https://kokunoyumeto.github.io/algebraic-topology-id/roberts-001-030-fomberg-001-007-ca01-hints-r01-r06-ca02-ca03-lab01-lab02-lab03-lab04-capstone/"
    pdf_url = "https://zenodo.org/records/22168033/files/00_TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_LAB03_LAB04_CAPSTONE_READER.pdf?download=1"
    source_backend_url = "https://zenodo.org/records/22168033/files/TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_LAB03_LAB04_CAPSTONE_EDITABLE_SOURCE_BACKEND.zip?download=1"
    qa_provenance_url = "https://zenodo.org/records/22168033/files/TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_LAB03_LAB04_CAPSTONE_QA_PROVENANCE.zip?download=1"
    require(html["public_url"] == html_url, "HTML learner route drift")
    pdf_surfaces = [row for row in tables["reader_surfaces"] if row["payload"].get("format") == "pdf"]
    require(len(pdf_surfaces) == 1 and pdf_surfaces[0]["payload"].get("primary") is False, "PDF primary/secondary boundary drift")
    require(pdf_surfaces[0]["payload"].get("public_url") == pdf_url, "PDF direct-download route drift")
    require(pdf_surfaces[0]["payload"].get("pages") == 564, "PDF page count drift")
    require("untagged" in pdf_surfaces[0]["payload"].get("accessibility_state", ""), "PDF accessibility limitation missing")
    require(all(row["payload"].get("unit_anchor") is None for row in tables["routes"]), "invented public unit anchor")

    route_urls = {row["payload"].get("public_url"): row["payload"] for row in tables["routes"]}
    require(route_urls.get(html_url, {}).get("machine_data_only") is False, "HTML route is not learner-facing")
    require(route_urls.get(pdf_url, {}).get("route_kind") == "verified_direct_file_download", "PDF route is not a direct download")

    public_artifacts = [row for row in tables["artifacts"] if row["payload"].get("publication_state") == "public_anonymous_readback_verified"]
    require(len(public_artifacts) == 4, "final public artifact census drift")
    expected_public = {
        "semantic_html_course": (16049720, "a17ce8e3e4d6b93de5e678ce38f3b7834c3b6a9ca1bff063fd3e879875e254a8", html_url),
        "offline_pdf_reader": (10376749, "d29dad39a06224a83aed11afdb4c65b317a45c6b900122dd40948df712ff8340", pdf_url),
        "editable_source_backend": (8406450, "f7670f6e6ad9a95ff808a1ddf4c2fdd8b41c6bce1916d33ac6fe5063be184b1b", source_backend_url),
        "qa_provenance": (2628497, "56cf8d60454622e654df4f238539791aa1b6a3e8884639bf39bad620c017a747", qa_provenance_url),
    }
    for row in public_artifacts:
        kind = row["payload"]["artifact_kind"]
        require((row["payload"]["bytes"], row["payload"]["sha256"], row["payload"]["public_url"]) == expected_public[kind], f"public artifact identity or direct URL drift: {kind}")

    integrated_relations = [row for row in tables["relations"] if row["payload"].get("native_relation_id") == "relation:xref:o012-d60:integrated-rights"]
    require(len(integrated_relations) == 1, "integrated course-rights relation missing")
    require(integrated_relations[0]["payload"].get("to_native_id") == "rights:o012-d60-integrated-route-cc-by-sa-4.0", "integrated rights target drift")
    require(integrated_relations[0]["payload"].get("to_projected_id") is not None, "integrated rights projection missing")
    require(all(row["payload"].get("flattened_course_license") is False for row in tables["rights"]), "component rights were flattened")

    forbidden = []
    for table_name, rows in tables.items():
        for ordinal, row in enumerate(rows, 1):
            forbidden.extend(recursively_forbidden_prose_keys(row, f"tables/{table_name}.jsonl:{ordinal}"))
    require(not forbidden, f"forbidden textbook-prose fields in adapter: {forbidden[:3]}")
    require(all(row["payload"].get("body_prose_copied") is False for row in tables["search_documents"]), "search projection copied body prose")
    require(all(row["payload"].get("body_prose_copied") is False for row in tables["content_bindings"]), "content binding copied body prose")

    capability = read_json(package / "capability-declarations-v0.2.0.json")
    limitations = {row["name"]: row["loss_gap_report"]["status"] for row in capability["capabilities"]}
    require(limitations == {
        "structure_localization": "closed",
        "terminology": "declared_limitation",
        "mathematical_preservation": "declared_limitation",
        "assessment_support": "declared_limitation",
        "assets": "declared_limitation",
        "accessibility": "declared_limitation",
        "corrections": "declared_limitation",
        "computational_interactives": "declared_limitation",
        "publication": "closed",
        "research_support": "declared_limitation",
    }, "capability limitation truth table drift")

    return {
        "schema_id": "program-matematika-indonesia/d60-v2.3.1-adapter-validation/1",
        "status": "PASS",
        "generic_validation": generic,
        "owner_native": {
            "files": 11,
            "records": 8338,
            "current_heads": sum(len(rows) for rows in native_heads.values()),
            "global_ids": len(all_native_ids),
            "relation_endpoints_resolved": 2886,
            "malformed_term_envelopes_declared": term_missing_envelope,
            "current_terminology_status_gaps_declared": current_term_missing_status,
        },
        "adapter": {
            "canonical_records": sum(observed_counts.values()),
            "materialized_native_bijections": 6279,
            "translation_rows": 2204,
            "csv_roundtrip": "pass",
            "learner_route": "verified_semantic_html_course_root",
            "unit_anchor_coverage": 0,
            "body_prose_copied": False,
            "component_rights_flattened": False,
        },
        "limitations_preserved": limitations,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--owner-package-root", type=Path, required=True)
    parser.add_argument("--build-a", type=Path)
    parser.add_argument("--build-b", type=Path)
    parser.add_argument("--report", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        report = validate_specific(args)
        if args.report:
            write_json(args.report, report)
        print(compact_json(report))
        return 0
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
