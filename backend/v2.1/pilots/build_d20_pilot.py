#!/usr/bin/env python3
"""Build the read-only D20 functional-analysis v2.1 pilot.

This adapter intentionally materializes only compact unit, relation, search,
rights/accessibility, and route-readback projections.  It never copies TeX or
HTML prose and never writes below the owner tree.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SCHEMA_ID = "interlanguage/global-backend-v2.1-unit-search-pilot/0.1.0"
RECORDED_AT = "2026-08-26T00:00:00Z"
PROGRAM_ROOT = Path(__file__).resolve().parents[3]
PILOTS_ROOT = Path(__file__).resolve().parent
OWNER_ROOT = PROGRAM_ROOT.parent
D20_ROOT = OWNER_ROOT / "functional-analysis-erdman-id"
D20_BACKEND = D20_ROOT / "backend"
RECEIPT = PROGRAM_ROOT / "backend/migrations/erdman-functional-analysis-id-v1/MIGRATION_RECEIPT.json"
OUT = PILOTS_ROOT / "d20-functional-analysis"

EXPECTED = {
    "receipt": "3ac413522ff07ac6dd0a625d23fe09863151c5d4d32bae793ded93810063493e",
    "units": "123ccce49922a7e9c4c2d6d4b3111837582ac6c13070eaba16e0531fecbfa8ca",
    "routes": "36fb1838ae99ad850c8f4832c318d64d87f5aee1eb22415583f4ec8178a7c0f5",
    "surfaces": "a7de54f540550144e06f26bd61310d1a639bb711b1e9f4cec884a72ee36f1a7a",
    "relations": "a4f61877605e942f69d5168c7242cd1ff7ac86de9fa207f06445e318e30bb24a",
    "semantic_units": "696275232f35ec159dc409b0e49133169f4ced0ee50919b7cd073ed4875d2604",
    "segments": "d9eae751204ac837aa6a98b8a0bb3880a2aec24e7d1f3656c45002a1e8031963",
    "formula_map": "e3dd86401ffeb10770e82dba020bf7dfdcbf05d1eb02c04cd1b2b1e3e86791fe",
    "html_assets": "1ba1b4d4e98addfb6a3d661a556afdff04683b6d0a801102d9a0144dc711d1f4",
    "rights": "fe2176f18b74e451f4589f72e015ccb3ac03fe20f51eaed989f7c36d244445b8",
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def json_load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSONL {path}:{number}") from exc


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.write_text("".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8", newline="\n")


def artifact(path: Path, root: Path, role: str) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "path": path.relative_to(root).as_posix(), "role": role, "sha256": sha256_path(path)}


def source_evidence(path: Path, role: str, locator_base: str = "owner_root") -> dict[str, Any]:
    if locator_base == "program_repository_root":
        locator = path.relative_to(PROGRAM_ROOT).as_posix()
    else:
        locator = path.relative_to(OWNER_ROOT).as_posix()
    return {"bytes": path.stat().st_size, "locator": locator, "locator_base": locator_base, "role": role, "sha256": sha256_path(path)}


def require_hash(path: Path, expected: str) -> None:
    actual = sha256_path(path)
    if actual != expected:
        raise ValueError(f"authority hash changed: {path}: {actual} != {expected}")


def search_text(*values: str | None) -> str:
    joined = " ".join(value for value in values if value)
    normalized = unicodedata.normalize("NFKC", joined).casefold()
    normalized = re.sub(r"[^0-9a-zà-öø-ÿā-ž]+", " ", normalized, flags=re.IGNORECASE)
    return " ".join(normalized.split())


def resolve_source(source_path: str) -> Path:
    if source_path.startswith("source/"):
        return D20_ROOT / source_path
    return D20_ROOT / "source/upstream" / source_path


def route_for_unit(row: dict[str, Any]) -> str | None:
    unit_id = row["id"]
    if unit_id == "FAOA-2015-PREFACE":
        return "prakata"
    match = re.fullmatch(r"FAOA-2015-CH(\d{2})", unit_id)
    return f"bab-{int(match.group(1)):02d}" if match else None


def unit_kind(unit_id: str) -> str:
    """Return a stable structural kind rather than the owner's generic row type."""
    if unit_id == "FAOA-2015-PREFACE":
        return "front_matter"
    if re.fullmatch(r"FAOA-2015-CH\d{2}", unit_id):
        return "chapter"
    if unit_id == "FAOA-ID-BRIDGE-CS":
        return "original_companion"
    return "unit"


def build() -> dict[str, Any]:
    require_hash(RECEIPT, EXPECTED["receipt"])
    for key, filename in (
        ("units", "units.jsonl"),
        ("routes", "html_routes.jsonl"),
        ("surfaces", "html_surfaces.jsonl"),
        ("relations", "relations.jsonl"),
        ("semantic_units", "semantic_units.jsonl"),
        ("segments", "segments.jsonl"),
        ("formula_map", "formula_map.jsonl"),
        ("html_assets", "html_assets.jsonl"),
        ("rights", "rights.jsonl"),
    ):
        require_hash(D20_BACKEND / filename, EXPECTED[key])

    receipt = json_load(RECEIPT)
    owner_units = list(jsonl(D20_BACKEND / "units.jsonl"))
    if len(owner_units) != 19:
        raise ValueError(f"D20 unit closure changed: {len(owner_units)}")
    owner_routes = list(jsonl(D20_BACKEND / "html_routes.jsonl"))
    routes_by_route: dict[str, list[dict[str, Any]]] = {}
    for route in owner_routes:
        routes_by_route.setdefault(route.get("route", ""), []).append(route)

    # Verify every admitted source/target binding and derive a compact root
    # unit record.  The original companion bridge is retained as an explicit
    # queued unit, with no invented learner route.
    units: list[dict[str, Any]] = []
    search_rows: list[dict[str, Any]] = []
    route_local_paths: set[str] = set()
    for row in sorted(owner_units, key=lambda item: (item.get("order", 10_000), item["id"])):
        unit_id = row["id"]
        route = route_for_unit(row)
        source_path = resolve_source(row["source_path"]) if row.get("source_path") else None
        target_path = D20_ROOT / row["target_path"] if row.get("target_path") else None
        if source_path is not None:
            if not source_path.exists() or source_path.stat().st_size != row["source_bytes"] or sha256_path(source_path) != row["source_sha256"]:
                raise ValueError(f"D20 source binding failed: {unit_id}")
        if target_path is not None:
            if not target_path.exists() or target_path.stat().st_size != row["target_bytes"] or sha256_path(target_path) != row["target_sha256"]:
                raise ValueError(f"D20 target binding failed: {unit_id}")

        route_rows = routes_by_route.get(route or "", [])
        local_html = D20_ROOT / "output/html" / route / "index.html" if route else None
        if route:
            if not route_rows or local_html is None or not local_html.exists():
                raise ValueError(f"D20 HTML route closure failed: {unit_id}")
            route_local_paths.add(local_html.relative_to(D20_ROOT).as_posix())
            route_row = sorted(route_rows, key=lambda item: item["href"])[0]
            route_href = route_row["href"]
            route_url = "https://kokunoyumeto.github.io/functional-analysis-erdman-id/output/html/" + route_href
            learner_route = {
                "anchor": route_row["id"],
                "anchor_evidence": {"href": route_row["href"], "id": route_row["id"], "route": route_row["route"]},
                "local_evidence_locator": local_html.relative_to(D20_ROOT).as_posix(),
                "local_evidence_sha256": sha256_path(local_html),
                "route_state": "owner_native_semantic_html_route_local_and_public_base_verified",
                "url": route_url,
            }
        else:
            learner_route = {
                "anchor": None,
                "route_state": "not_yet_authored_no_route_in_owner_surface",
                "url": None,
            }

        native_locator = {
            "source_path": row.get("source_path"),
            "target_path": row.get("target_path"),
            "source_locator_state": "owner-native source/target file bytes are hash-bound; source prose is not copied into pilot",
        }
        unit = {
            "artifact_bytes": row.get("artifact_bytes"),
            "artifact_pages": row.get("artifact_pages"),
            "artifact_sha256": row.get("artifact_sha256"),
            "course_id": "D20",
            "edition_id": row.get("edition_id"),
            "learner_route": learner_route,
            "locale": "id-ID",
            "native_locator": native_locator,
            "native_unit_id": unit_id,
            "native_unit_kind": unit_kind(unit_id),
            "order_index": row.get("order"),
            "order_key": f"{row.get('order', 0):04d}" if isinstance(row.get("order"), int) else "9999",
            "record_type": "unit",
            "rights_component_id": row.get("rights_id"),
            "schema_id": SCHEMA_ID,
            "source_bytes": row.get("source_bytes"),
            "source_lines": row.get("source_lines"),
            "source_sha256": row.get("source_sha256"),
            "stable_unit_id": unit_id,
            "target_bytes": row.get("target_bytes"),
            "target_lines": row.get("target_lines"),
            "target_sha256": row.get("target_sha256"),
            "title": row.get("target_title") or row.get("title"),
            "translation_state": row.get("translation_state", row.get("authoring_state")),
        }
        units.append(unit)
        title = unit["title"] or unit_id
        search_rows.append(
            {
                "course_id": "D20",
                "learner_url": learner_route["url"],
                "locale": "id-ID",
                "native_unit_kind": unit["native_unit_kind"],
                "order_key": unit["order_key"],
                "record_type": "search_document",
                "search_text": search_text("Analisis Fungsional dan Aljabar Operator", title, unit_id),
                "stable_unit_id": unit_id,
                "title": title,
            }
        )

    selected_ids = {row["id"] for row in owner_units}
    relations: list[dict[str, Any]] = []
    for row in jsonl(D20_BACKEND / "relations.jsonl"):
        if row.get("from_id") not in selected_ids:
            continue
        evidence = {key: value for key, value in row.items() if key not in {"from_id", "to_id", "id", "record_type", "relation_type", "schema", "schema_version"}}
        evidence["native_relation_id"] = row["id"]
        relations.append(
            {
                "evidence": evidence,
                "from_id": row["from_id"],
                "record_type": "relation",
                "relation_type": row["relation_type"],
                "strength": "hard",
                "to_id": row["to_id"],
            }
        )
    relations.sort(key=lambda item: (item["relation_type"], item["from_id"], item["to_id"], item["evidence"]["native_relation_id"]))
    unit_ids = {row["stable_unit_id"] for row in units}
    external_relation_endpoints = sorted(
        ({row["from_id"] for row in relations} | {row["to_id"] for row in relations}) - unit_ids
    )

    rights_rows = list(jsonl(D20_BACKEND / "rights.jsonl"))
    surface = next(row for row in jsonl(D20_BACKEND / "html_surfaces.jsonl") if row.get("id") == "FAOA-2015-ID-HTML-SOURCE-TEXT")
    asset_rows = list(jsonl(D20_BACKEND / "html_assets.jsonl"))
    semantic_count = sum(1 for _ in jsonl(D20_BACKEND / "semantic_units.jsonl"))
    segment_count = sum(1 for _ in jsonl(D20_BACKEND / "segments.jsonl"))
    formula_count = sum(1 for _ in jsonl(D20_BACKEND / "formula_map.jsonl"))
    rights_accessibility = {
        "accessibility": {
            "citation_count": surface["citation_count"],
            "diagram_count": surface["diagram_count"],
            "formula_count": formula_count,
            "html_asset_count": len(asset_rows),
            "html_mathml_count": surface["mathml_count"],
            "html_route_count": surface["route_records"],
            "html_semantic_unit_count": semantic_count,
            "html_segment_count": segment_count,
            "state": "owner-native semantic HTML and accessibility metadata are summarized by exact hashes; prose and SVG payloads remain zero-copy",
        },
        "course_id": "D20",
        "rights": {
            "components": rights_rows,
            "state": "all owner-native rights rows retained; excluded/unclear components are not flattened or silently relicensed",
        },
        "schema_id": SCHEMA_ID,
    }

    # These are deterministic observations made against the public deployment
    # during this pilot.  They make the short-route gap explicit while binding
    # the proven /output/html route base; no route is invented here.
    route_gap = {
        "course_id": "D20",
        "observed_at": RECORDED_AT,
        "public_base": "https://kokunoyumeto.github.io/functional-analysis-erdman-id/",
        "proven_route_base": "https://kokunoyumeto.github.io/functional-analysis-erdman-id/output/html/",
        "observations": [
            {"bytes": 1413, "sha256": "8dce05e364b31250293133780512f6da64da12995e87b96b78777c36f8b00edb", "status": 200, "url": "https://kokunoyumeto.github.io/functional-analysis-erdman-id/"},
            {"bytes": 375668, "sha256": "37cb4c55ba8c6dfb442319b9020865bb75e53eb56ccfc2fdc55dfc387941a5e8", "status": 200, "url": "https://kokunoyumeto.github.io/functional-analysis-erdman-id/output/html/bab-01/index.html"},
            {"bytes": 84450, "sha256": "1b46d0caad54f0aa32b53b3f254139f488dd837a930dff257437b4ac55957d18", "status": 200, "url": "https://kokunoyumeto.github.io/functional-analysis-erdman-id/output/html/prakata/index.html"},
            {"status": 404, "url": "https://kokunoyumeto.github.io/functional-analysis-erdman-id/bab-01/"},
            {"status": 200, "url": "https://kokunoyumeto.github.io/functional-analysis-erdman-id/output/html-companion/solusi-bab-01/index.html"},
        ],
        "route_gap": "short /bab-N/ paths are not learner routes; central wrappers must link to the proven /output/html/{route}/index.html paths. Companion output has a separate /output/html-companion/ tree.",
        "source_receipt_sha256": EXPECTED["receipt"],
        "schema_id": SCHEMA_ID,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    write_jsonl(OUT / "units.jsonl", units)
    write_jsonl(OUT / "relations.jsonl", relations)
    write_jsonl(OUT / "search.jsonl", search_rows)
    write_json(OUT / "rights_accessibility.json", rights_accessibility)
    write_json(OUT / "route_gap_report.json", route_gap)
    files = [
        artifact(OUT / "relations.jsonl", OUT, "evidence_bound_relations"),
        artifact(OUT / "rights_accessibility.json", OUT, "rights_accessibility_summary"),
        artifact(OUT / "route_gap_report.json", OUT, "learner_route_readback_evidence"),
        artifact(OUT / "route_proposal.json", OUT, "frozen_central_route_proposal"),
        artifact(OUT / "search.jsonl", OUT, "compact_search_shard"),
        artifact(OUT / "units.jsonl", OUT, "stable_unit_registry"),
    ]
    route_count = len(route_local_paths)
    manifest = {
        "canonical_serialization": "UTF-8; JSON objects sorted by key; JSONL LF with trailing newline",
        "course_id": "D20",
        "dataset_id": "pilot:d20-functional-analysis:v2.1:0.1.0",
        "files": files,
        "input_authority": [
            source_evidence(RECEIPT, "admitted_migration_receipt", "program_repository_root"),
            source_evidence(D20_BACKEND / "units.jsonl", "owner_native_units", "owner_root"),
            source_evidence(D20_BACKEND / "html_routes.jsonl", "owner_native_html_route_map", "owner_root"),
            source_evidence(D20_BACKEND / "html_surfaces.jsonl", "owner_native_html_surface", "owner_root"),
            source_evidence(D20_BACKEND / "semantic_units.jsonl", "owner_native_semantic_units", "owner_root"),
            source_evidence(D20_BACKEND / "segments.jsonl", "owner_native_segments", "owner_root"),
            source_evidence(D20_BACKEND / "relations.jsonl", "owner_native_relations", "owner_root"),
            source_evidence(D20_BACKEND / "formula_map.jsonl", "owner_native_formula_map", "owner_root"),
            source_evidence(D20_BACKEND / "html_assets.jsonl", "owner_native_html_assets", "owner_root"),
            source_evidence(D20_BACKEND / "rights.jsonl", "owner_native_rights", "owner_root"),
        ],
        "limitations": [
            "The original companion bridge unit is queued and has no learner route; no route is invented.",
            "Public deployment evidence proves the root and /output/html route base; short /bab-N/ paths are 404 and must not be emitted as learner links.",
            "TeX, HTML, SVG, and accessibility prose are not copied; records bind owner bytes by path, size, and SHA-256.",
            "Owner html_surface remains publication_state=pending/whole_edition_state=in_progress; this pilot reports sampled route readback and does not upgrade edition state.",
        ],
        "materialization_scope": "compact root-unit, relation, search, rights/accessibility, and route-readback projections; no prose",
        "native_backend_contribution": {
            "accessibility": "80 admitted HTML asset descriptions, 11,193 MathML occurrences, 2,104 index occurrences, and 1,867 semantic units summarized without payload duplication",
            "identity_and_order": "17 chapter roots plus preface and queued original companion bridge, bound to owner units.jsonl",
            "route": f"{route_count} owner-native HTML root pages locally hash-verified; public route-base observations recorded separately",
            "source_target_binding": "every admitted file unit source/target pair is checked against owner-native bytes and hashes",
        },
        "owner_tree_mode": "read_only",
        "relation_endpoint_policy": {
            "external_endpoint_count": len(external_relation_endpoints),
            "external_endpoint_sha256": sha256_text(canonical_json(external_relation_endpoints)),
            "mode": "exact_external_set",
        },
        "record_counts": {
            "relations": len(relations),
            "rights_accessibility_documents": 1,
            "route_readback_documents": 1,
            "search_documents": len(search_rows),
            "units": len(units),
        },
        "recorded_at": RECORDED_AT,
        "schema_id": SCHEMA_ID,
        "uncertain_field_contracts": [
            {"field": "learner_route.url", "decision": "use only proven /output/html/{route}/index.html paths; short /bab-N/ paths are explicitly excluded by route_gap_report"},
            {"field": "FAOA-ID-BRIDGE-CS route", "decision": "null until the separately authored companion is admitted and rendered"},
        ],
    }
    write_json(OUT / "manifest.json", manifest)
    return manifest


def main() -> None:
    manifest = build()
    print(canonical_json({"result": "pass", "course_id": "D20", "record_counts": manifest["record_counts"]}))


if __name__ == "__main__":
    main()
