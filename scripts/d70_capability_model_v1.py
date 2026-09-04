#!/usr/bin/env python3
"""Shared deterministic model and invariants for the D70 thin adapter.

This module deliberately uses only the Python standard library and keeps only
the comparatively small adapter projections in memory.  It never loads PDF,
TeX, image, or archive payloads.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


CONTRACT = "course-learning-capability/1"
COURSE_ID = "D70"
SCHEMA_PREFIX = "d70-capability"
EXPECTED_LI_ORDERS = tuple(range(1, 36)) + tuple(range(43, 49))
EXPECTED_COMPONENT_IDS = ("O013-K01", "O013-K02", "O013-K03", "O013-K04")
EXPECTED_ROUTE_IDS = tuple(
    [f"O013-P{i:02d}" for i in range(1, 7)]
    + [f"O013-R{i}" for i in range(10, 17)]
    + [f"O013-C{i}" for i in range(10, 16)]
    + ["O013-S10"]
)
EXPECTED_STAGE_IDS = tuple(f"O013-Q{i:02d}" for i in range(1, 8))
EXPECTED_DIAGNOSTIC_IDS = tuple(f"O013-D{i:02d}" for i in range(1, 9))
EXPECTED_MASTERY_IDS = tuple(f"O013-M{i:02d}" for i in range(1, 9))
EXPECTED_NATIVE_RIGHTS_IDS = frozenset(
    {
        "urn:uuid:0baf6c47-021d-5310-9475-81519e710250",
        "urn:uuid:10faf5cd-990f-5850-87b4-26922b062485",
        "urn:uuid:624ac6e0-0ed9-531c-8b35-47c040240806",
        "urn:uuid:b9f7a7a7-8e18-507a-b72e-b5de733a7430",
        "urn:uuid:e18339ae-66cd-5304-b544-b220dd41380d",
    }
)
EXPECTED_ADAPTER_RIGHTS_IDS = frozenset(
    {
        "d70:rights:external-tex-packages",
        "d70:rights:duncan",
        "d70:rights:cring",
        "d70:rights:original-route",
    }
)
EXPECTED_LI_NAMED_ADJUSTMENT_IDS = frozenset(
    """
O013-LI-U004-COR-001 O013-LI-U005-CLR-001 O013-LI-U005-COR-001
O013-LI-U005-READER-COR-001 O013-LI-U006-COR-001 O013-LI-U007-COR-001
O013-LI-U014-COR-001 O013-LI-U014-COR-002 O013-LI-U014-COR-003 O013-LI-U014-COR-004
O013-LI-U015-COR-001 O013-LI-U015-COR-002
O013-LI-U016-COR-001 O013-LI-U016-COR-002 O013-LI-U016-COR-003
O013-LI-U017-COR-001 O013-LI-U017-COR-002 O013-LI-U017-COR-003 O013-LI-U017-COR-004 O013-LI-U017-COR-005 O013-LI-U017-COR-006
O013-LI-U018-COR-001 O013-LI-U018-COR-002 O013-LI-U019-COR-001 O013-LI-U020-COR-001
O013-LI-U021-COR-001 O013-LI-U021-COR-002 O013-LI-U021-ED-001
O013-LI-U022-COR-001 O013-LI-U022-COR-002 O013-LI-U023-ED-001 O013-LI-U024-COR-001
O013-LI-U025-COR-001 O013-LI-U026-COR-001 O013-LI-U026-COR-002 O013-LI-U026-COR-003 O013-LI-U026-COR-004
O013-LI-U027-COR-001 O013-LI-U027-COR-002 O013-LI-U028-COR-001 O013-LI-U030-COR-001 O013-LI-U031-COR-001
O013-LI-U032-COR-001 O013-LI-U032-COR-002 O013-LI-U033-COR-001 O013-LI-U033-COR-002 O013-LI-U034-COR-001
O013-LI-U035-COR-001 O013-LI-U036-COR-001 O013-LI-U036-COR-002 O013-LI-U037-COR-001
O013-LI-U038-COR-001 O013-LI-U038-COR-002 O013-LI-U039-COR-001 O013-LI-U039-COR-002 O013-LI-U040-COR-001
O013-LI-U041-COR-001 O013-LI-U041-COR-002 O013-LI-U041-COR-003 O013-LI-U041-COR-004
O013-LI-U042-COR-001 O013-LI-U042-COR-002 O013-LI-U042-COR-003 O013-LI-U042-COR-004 O013-LI-U042-COR-005 O013-LI-U042-COR-006 O013-LI-U042-COR-007
O013-LI-U043-COR-001 O013-LI-U043-COR-002
""".split()
)
EXPECTED_LI_CORRECTION_IDS = EXPECTED_LI_NAMED_ADJUSTMENT_IDS | {
    "urn:uuid:2cf9847b-7718-54e7-8f21-778d1a4785f7",
    "d70:li-adjustment:unit-014-equation-numbering",
}
ROUTE_ROOT_MAP = {
    "O013-R10": "root.rep_intro",
    "O013-R11": "root.lin_alg",
    "O013-R12": "root.modules",
    "O013-R13": "root.characters",
    "O013-R14": "root.induction",
    "O013-R15": "root.symmetric",
    "O013-R16": "root.nonclosed",
    "O013-C10": "root.cring.nakayama",
    "O013-C11": "root.cring.spec_zariski",
    "O013-C12": "root.cring.associated_primary",
    "O013-C13": "root.cring.lying_over_going_up",
    "O013-C14": "root.cring.nullstellensatz_normalization",
    "O013-C15": "root.cring.krull_dimension",
}
PUBLIC_RECORD = {
    "repository": "https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id",
    "content_commit": "91b76d0381aa0d4c6614ad6556fe779fe8039f93",
    "content_tree": "a017f0a2efc016d1a2b6b422577de77e0db9b6ac",
    "receipt_commit": "26e6f531e9309e83998325a8c7b705e92d293287",
    "receipt_tree": "cd1006dd85248c6b76d3cb1623c7049837a91cd1",
    "record_id": 22160944,
    "doi": "10.5281/zenodo.22160944",
    "concept_doi": "10.5281/zenodo.22160943",
    "file_count": 9,
    "total_bytes": 5_155_778,
}
PUBLIC_FILES = {
    "01_metode-aljabar-jilid-1-id-lengkap.pdf": (2_875_853, "c2994530e3da1711d44f8c36315c40874e87f1968d1a81c1432105de2251c2ee"),
    "02_catatan-teori-representasi-duncan-id.pdf": (508_546, "6779d6467463fde4ef0b4fae147dc63533dff0919eda684120d409f1f5f07d12"),
    "03_pilihan-aljabar-komutatif-cring-id.pdf": (378_716, "4596fd6a84f829e1e9c14cb87468226d6ef49c653d41886af5fab9f2bd96b5db"),
    "04_o013-rute-pembelajar-dan-penguasaan-id.pdf": (79_365, "31af67adf897519a1fef0ed53757c2a3d9d12b5ccc3bdd4cb74e9ce01dd27a18"),
    "05_o013-sumber-backend-1.0.0.zip": (1_295_518, "6273206ffb42277f3040d638e1a0f0870596b823a239fa9d3947d964aa094ef9"),
    "LICENSES.md": (3_723, "5185c0b42b59e38bb4533fb902c12f3d31061c773fd6d5bcd9fb84be18bd1cbf"),
    "o013-aggregate-manifest.schema.json": (4_840, "70de69436b93ded48fd1b94791c0b56efa98a94f5c7ce01e08281b14404813a6"),
    "o013-aggregate-manifest.json": (8_406, "3f19fd77fe9b5d54b6efa6b3558f02c704f2e16504315444edcdfc7fd40c089c"),
    "SHA256SUMS.txt": (811, "ec4cca7cb9277fe339f0269195e9f102251e9f3f5b6a4be45fa30c2ca8d3799a"),
}
PUBLIC_DOWNLOAD_BASE = "https://zenodo.org/api/records/22160944/files/"
SOURCE_CATALOG = {
    "path": "publication/o013-aggregate-1.0.0/o013-aggregate-manifest.json",
    "bytes": 8_406,
    "sha256": "3f19fd77fe9b5d54b6efa6b3558f02c704f2e16504315444edcdfc7fd40c089c",
    "url": PUBLIC_DOWNLOAD_BASE + "o013-aggregate-manifest.json/content",
}
CENTRAL_CAPSULE_RECORD = {
    "bytes": 5_462,
    "sha256": "c28e241f6a3712469096c1a51dfc51078e8696c5e482ccffe06218a5c6e97514",
}
CENTRAL_COVERAGE_RECORD = {
    "bytes": 2_758,
    "sha256": "b96a03af730fa6976d7356b37501212415a2a0a4c5d0e0da9bcfb576bedc4b62",
}
SHARED_SCHEMA = {
    "path": "schemas/course-capsule-v1/course-learning-capability-v1.schema.json",
    "bytes": 3_954,
    "sha256": "0f1af9f2bf4eda55e6d2d9a9a528c88a93d9a54c1ef6102503c99b32e65da09e",
}
EXPECTED_COUNTS = {
    "components": 4,
    "pages": 716,
    "native_roots": 54,
    "li_roots": 41,
    "duncan_roots": 7,
    "cring_roots": 6,
    "units": 20,
    "relations": 36,
    "stages": 7,
    "stage_memberships": 36,
    "diagnostics": 8,
    "diagnostic_targets": 14,
    "diagnostic_expected_answers": 8,
    "diagnostic_points": 8,
    "mastery": 8,
    "mastery_targets": 13,
    "mastery_hints": 16,
    "mastery_answers": 8,
    "terms": 690,
    "terms_admitted": 689,
    "terms_provisional": 1,
    "corrections": 80,
    "li_adjustments": 71,
    "cring_repairs": 9,
    "original_bridges": 3,
    "rights": 9,
}
NEGATIVE_CASES = {
    "collapse-four-components": ("D70-COMPONENT-BOUNDARY", "D70-COMPONENT-RIGHTS", "D70-SOURCE-LOCALES"),
    "blanket-license": ("D70-BLANKET-LICENSE",),
    "claim-full-cring": ("D70-CRING-SELECTION",),
    "include-duncan-assignments": ("D70-DUNCAN-BOUNDARY",),
    "renumber-li-units": ("D70-LI-UNIT-ORDER",),
    "claim-li-142-exercises": ("D70-LI-EXERCISE-TRUTH",),
    "claim-li-49-hints": ("D70-LI-HINT-TRUTH",),
    "admit-provisional-valuation": ("D70-VALUATION-PROVISIONAL",),
    "drop-provisional-valuation": ("D70-TERMINOLOGY-SET", "D70-VALUATION-PROVISIONAL"),
    "claim-source-solutions": ("D70-SOURCE-SOLUTIONS",),
    "expose-learner-answer": ("D70-STAGED-DISCLOSURE",),
    "claim-native-html": ("D70-NATIVE-HTML",),
    "claim-native-mathml": ("D70-NATIVE-MATHML",),
    "claim-tagged-pdf": ("D70-PDF-TAGGED",),
    "claim-wcag": ("D70-WCAG",),
    "claim-assistive-testing": ("D70-ASSISTIVE-TESTING",),
    "claim-full-native-roundtrip": ("D70-NATIVE-ROUNDTRIP",),
    "claim-pdf-byte-replay": ("D70-PDF-BYTE-REPLAY",),
    "stale-publication-state": ("D70-PUBLIC-STATE",),
    "drop-route-stage": ("D70-STAGE-SET",),
    "drop-route-node": ("D70-ROUTE-AUTHORSHIP", "D70-ROUTE-EDGES", "D70-ROUTE-NODE-SET"),
    "alter-route-edge": ("D70-ROUTE-EDGES",),
    "drop-diagnostic": ("D70-DIAGNOSTIC-SET", "D70-SHARED-ASSESSMENTS"),
    "drop-mastery": ("D70-MASTERY-ANSWERS", "D70-MASTERY-HINTS", "D70-MASTERY-SET"),
    "drop-mastery-hint": ("D70-MASTERY-HINTS",),
    "drop-mastery-answer": ("D70-MASTERY-ANSWERS",),
    "fabricate-root-map": ("D70-ROOT-MAP",),
    "drop-rights-record": ("D70-RIGHTS-SET",),
    "copy-native-body": ("D70-ZERO-COPY",),
    "flatten-source-locale": ("D70-SOURCE-LOCALES",),
    "alter-public-artifact-hash": ("D70-PUBLIC-IDENTITY",),
    "drop-li-adjustment": ("D70-CORRECTION-SET", "D70-LI-ADJUSTMENTS"),
    "treat-cring-bridge-as-source": ("D70-CRING-BRIDGE-PROVENANCE",),
}


class D70Error(ValueError):
    pass


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def canonical_json_compact(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_json_line(value: Any) -> bytes:
    return canonical_json_compact(value) + b"\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": sha256_bytes(data)}


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path: Path, value: Any) -> None:
    write_bytes(path, canonical_json(value))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    write_bytes(path, b"".join(canonical_json_line(row) for row in rows))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


BUNDLE_FILES = {
    "course": ("data/course.json", "json"),
    "components": ("data/components.jsonl", "jsonl"),
    "native_roots": ("data/native-roots.jsonl", "jsonl"),
    "units": ("data/units.jsonl", "jsonl"),
    "routes": ("data/routes.jsonl", "jsonl"),
    "relations": ("data/relations.jsonl", "jsonl"),
    "stages": ("data/stages.jsonl", "jsonl"),
    "diagnostics": ("data/diagnostics.jsonl", "jsonl"),
    "mastery": ("data/mastery.jsonl", "jsonl"),
    "policies": ("data/policies.json", "json"),
    "rights": ("data/rights.jsonl", "jsonl"),
    "terminology": ("data/terminology.jsonl", "jsonl"),
    "corrections": ("data/corrections.jsonl", "jsonl"),
    "original_bridges": ("data/original-bridges.jsonl", "jsonl"),
    "capabilities": ("data/capabilities.json", "json"),
    "evidence": ("data/evidence.json", "json"),
    "learning_map": ("data/learning-map.json", "json"),
}


def load_bundle(output_root: Path) -> dict[str, Any]:
    bundle: dict[str, Any] = {}
    for key, (relative, kind) in BUNDLE_FILES.items():
        path = output_root / relative
        bundle[key] = read_jsonl(path) if kind == "jsonl" else read_json(path)
    return bundle


def _add(errors: list[str], condition: bool, code: str) -> None:
    if not condition:
        errors.append(code)


def _ids(rows: list[dict[str, Any]], key: str = "id") -> list[str]:
    return [str(row.get(key, "")) for row in rows]


def validate_bundle(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    components = bundle["components"]
    _add(errors, len(components) == 4 and tuple(_ids(components, "component_id")) == EXPECTED_COMPONENT_IDS and sum(int(x.get("pages", 0)) for x in components) == 716, "D70-COMPONENT-BOUNDARY")
    _add(errors, all(not x.get("blanket_license_claimed", False) for x in components) and bundle["course"].get("aggregate_license") == "component_specific", "D70-BLANKET-LICENSE")
    cring = next((x for x in components if x.get("component_id") == "O013-K03"), {})
    _add(errors, cring.get("selection_scope") == "six_exact_spans_74_pages_not_full_work", "D70-CRING-SELECTION")
    duncan = next((x for x in components if x.get("component_id") == "O013-K02"), {})
    excluded = duncan.get("excluded_external_assignments", {})
    _add(errors, excluded == {"assignment_sheets": 6, "problems": 49, "partial_solutions": 1, "included": False}, "D70-DUNCAN-BOUNDARY")

    roots = bundle["native_roots"]
    li_roots = [x for x in roots if x.get("component_id") == "O013-K01"]
    duncan_roots = [x for x in roots if x.get("component_id") == "O013-K02"]
    cring_roots = [x for x in roots if x.get("component_id") == "O013-K03"]
    _add(errors, len(roots) == 54 and len(set(_ids(roots, "native_root_id"))) == 54, "D70-NATIVE-ROOT-SET")
    _add(errors, tuple(x.get("source_order") for x in li_roots) == EXPECTED_LI_ORDERS and len(li_roots) == 41, "D70-LI-UNIT-ORDER")
    _add(errors, len(duncan_roots) == 7 and len(cring_roots) == 6, "D70-NATIVE-ROOT-SET")
    _add(errors, all(not any(k in x for k in ("body", "content", "tex", "source_text", "target_text")) for x in roots), "D70-ZERO-COPY")

    units = bundle["units"]
    unit_ids = tuple(_ids(units))
    _add(errors, len(units) == 20 and unit_ids == EXPECTED_ROUTE_IDS, "D70-ROUTE-NODE-SET")
    unit_map = {x.get("id"): x for x in units}
    p_rows = [unit_map.get(f"O013-P{i:02d}", {}) for i in range(1, 7)]
    _add(errors, all(x.get("mapping_state") == "component_level_only_unmapped" and x.get("component_id") == "O013-K04" and x.get("authored_component_id") == "O013-K04" and x.get("mapped_reader_component_id") == "O013-K01" and x.get("native_root_ids") == [] for x in p_rows), "D70-ROOT-MAP")
    _add(errors, all(unit_map.get(k, {}).get("native_root_ids") == [v] and unit_map.get(k, {}).get("mapping_provenance") == "adapter_derived_crosswalk" and unit_map.get(k, {}).get("authored_component_id") == "O013-K04" for k, v in ROUTE_ROOT_MAP.items()), "D70-ROOT-MAP")
    _add(errors, all(x.get("component_id") == "O013-K04" and x.get("authorship") == "edition_original_route_layer_not_source_component_authorship" for x in units), "D70-ROUTE-AUTHORSHIP")

    routes = bundle["routes"]
    _add(errors, len(routes) == 20 and tuple(_ids(routes)) == EXPECTED_ROUTE_IDS, "D70-ROUTE-NODE-SET")
    relation_pairs = {(x.get("from"), x.get("to")) for x in bundle["relations"]}
    expected_pairs = {(dep, row["id"]) for row in routes for dep in row.get("requires", [])}
    _add(errors, len(bundle["relations"]) == 36 and len(relation_pairs) == 36 and relation_pairs == expected_pairs, "D70-ROUTE-EDGES")

    stages = bundle["stages"]
    _add(errors, len(stages) == 7 and tuple(_ids(stages)) == EXPECTED_STAGE_IDS and sum(len(x.get("items", [])) for x in stages) == 36, "D70-STAGE-SET")
    diagnostics = bundle["diagnostics"]
    _add(errors, len(diagnostics) == 8 and tuple(_ids(diagnostics)) == EXPECTED_DIAGNOSTIC_IDS and sum(len(x.get("targets", [])) for x in diagnostics) == 14, "D70-DIAGNOSTIC-SET")
    _add(errors, len([x for x in diagnostics if x.get("expected")]) == 8 and sum(int(x.get("points", 0)) for x in diagnostics) == 8, "D70-DIAGNOSTIC-SET")
    mastery = bundle["mastery"]
    _add(errors, len(mastery) == 8 and tuple(_ids(mastery)) == EXPECTED_MASTERY_IDS and sum(len(x.get("targets", [])) for x in mastery) == 13, "D70-MASTERY-SET")
    _add(errors, sum(len(x.get("hints", [])) for x in mastery) == 16, "D70-MASTERY-HINTS")
    _add(errors, sum(1 for x in mastery if x.get("answer", {}).get("id") and x.get("answer", {}).get("text")) == 8, "D70-MASTERY-ANSWERS")

    terms = bundle["terminology"]
    _add(errors, len(terms) == 690 and len(set((x.get("source_term"), x.get("scope")) for x in terms)) == 690, "D70-TERMINOLOGY-SET")
    valuation = [x for x in terms if x.get("source_term") == "valuation" and x.get("target_term") == "valuasi" and x.get("scope") == "chapter 10"]
    _add(errors, len(valuation) == 1 and valuation[0].get("status") == "provisional" and sum(x.get("status") == "provisional" for x in terms) == 1 and sum(x.get("status") == "admitted" for x in terms) == 689, "D70-VALUATION-PROVISIONAL")

    corrections = bundle["corrections"]
    li_adjustments = [x for x in corrections if x.get("component_id") == "O013-K01"]
    cring_repairs = [x for x in corrections if x.get("component_id") == "O013-K03"]
    _add(errors, len(corrections) == 80 and len(cring_repairs) == 9, "D70-CORRECTION-SET")
    _add(errors, len(li_adjustments) == 71 and set(_ids(li_adjustments, "correction_id")) == EXPECTED_LI_CORRECTION_IDS, "D70-LI-ADJUSTMENTS")
    bridges = bundle["original_bridges"]
    _add(errors, len(bridges) == 3 and all(x.get("provenance") == "edition-original" and x.get("authorship") == "adapter_or_edition_original_not_source_author" for x in bridges), "D70-CRING-BRIDGE-PROVENANCE")

    rights = bundle["rights"]
    rights_ids = frozenset(_ids(rights, "rights_id"))
    _add(errors, len(rights) == 9 and rights_ids == EXPECTED_NATIVE_RIGHTS_IDS | EXPECTED_ADAPTER_RIGHTS_IDS, "D70-RIGHTS-SET")
    component_licenses = {x.get("component_id"): x.get("license_expression") for x in components}
    _add(errors, component_licenses == {
        "O013-K01": "CC-BY-4.0 with separately identified embedded/build-closure rights in LICENSES.md",
        "O013-K02": "CC-BY-4.0",
        "O013-K03": "GFDL-1.2-or-later; no invariant sections or cover texts",
        "O013-K04": "CC-BY-4.0",
    }, "D70-COMPONENT-RIGHTS")

    capabilities = bundle["capabilities"]
    corpus_truth = capabilities.get("li_corpus_truth", {})
    _add(errors, corpus_truth.get("top_level_exercises") == 161 and corpus_truth.get("backend_scalar_exercises") == 142, "D70-LI-EXERCISE-TRUTH")
    _add(errors, corpus_truth.get("hints") == 51 and corpus_truth.get("backend_scalar_hints") == 49, "D70-LI-HINT-TRUTH")
    _add(errors, capabilities.get("source_support", {}).get("solutions") == 0, "D70-SOURCE-SOLUTIONS")
    _add(errors, capabilities.get("learner", {}).get("answers_staged_in_closed_details") is True, "D70-STAGED-DISCLOSURE")
    accessibility = capabilities.get("accessibility", {})
    _add(errors, accessibility.get("native_semantic_html") is False, "D70-NATIVE-HTML")
    _add(errors, accessibility.get("native_mathml") is False, "D70-NATIVE-MATHML")
    _add(errors, accessibility.get("tagged_pdf_claimed") is False, "D70-PDF-TAGGED")
    _add(errors, accessibility.get("wcag_conformance_claimed") is False, "D70-WCAG")
    _add(errors, accessibility.get("assistive_technology_testing_claimed") is False, "D70-ASSISTIVE-TESTING")
    reproduction = capabilities.get("reproducibility", {})
    _add(errors, reproduction.get("full_native_roundtrip") is False, "D70-NATIVE-ROUNDTRIP")
    _add(errors, reproduction.get("pdf_byte_replay") is False, "D70-PDF-BYTE-REPLAY")
    _add(errors, tuple(x.get("source_locale") for x in components) == ("zh-Hans", "en", "en", "id-ID"), "D70-SOURCE-LOCALES")

    evidence = bundle["evidence"]
    _add(errors, all(evidence.get(k) == v for k, v in PUBLIC_RECORD.items()), "D70-PUBLIC-STATE")
    public_rows = evidence.get("public_files", [])
    public_files = {x.get("name"): (x.get("bytes"), x.get("sha256")) for x in public_rows}
    _add(errors, len(public_rows) == 9 and len(public_files) == 9 and public_files == PUBLIC_FILES, "D70-PUBLIC-IDENTITY")

    learning = bundle["learning_map"]
    _add(errors, learning.get("contract") == CONTRACT and learning.get("course_id") == COURSE_ID and len(learning.get("units", [])) == 20 and len(learning.get("prerequisite_routes", [])) == 36, "D70-SHARED-CONTRACT")
    _add(errors, learning.get("labs") == [] and learning.get("environments") == [] and len(learning.get("artifacts", [])) == 5 and len(learning.get("sources", [])) == 4 and len(learning.get("external_relation_nodes", [])) == 54, "D70-SHARED-CONTRACT")
    _add(errors, learning.get("source_catalog") == SOURCE_CATALOG, "D70-SHARED-CONTRACT")
    shared_exercises = [exercise for unit in learning.get("units", []) for exercise in unit.get("exercises", [])]
    _add(errors, len(shared_exercises) == 16 and len(set(_ids(shared_exercises))) == 16 and set(_ids(shared_exercises)) == set(EXPECTED_DIAGNOSTIC_IDS) | set(EXPECTED_MASTERY_IDS), "D70-SHARED-ASSESSMENTS")
    _add(errors, all({component.get("id") for component in unit.get("components", [])} >= {"O013-K04", unit_map.get(unit.get("id"), {}).get("mapped_reader_component_id")} for unit in learning.get("units", [])), "D70-ROUTE-AUTHORSHIP")
    return sorted(set(errors))


def apply_negative_mutation(bundle: dict[str, Any], mutation: str) -> dict[str, Any]:
    result = copy.deepcopy(bundle)
    if mutation == "collapse-four-components":
        result["components"] = result["components"][:3]
    elif mutation == "blanket-license":
        result["course"]["aggregate_license"] = "CC-BY-4.0"
    elif mutation == "claim-full-cring":
        next(x for x in result["components"] if x["component_id"] == "O013-K03")["selection_scope"] = "full_work"
    elif mutation == "include-duncan-assignments":
        next(x for x in result["components"] if x["component_id"] == "O013-K02")["excluded_external_assignments"]["included"] = True
    elif mutation == "renumber-li-units":
        next(x for x in result["native_roots"] if x["component_id"] == "O013-K01" and x["source_order"] == 43)["source_order"] = 36
    elif mutation == "claim-li-142-exercises":
        result["capabilities"]["li_corpus_truth"]["top_level_exercises"] = 142
    elif mutation == "claim-li-49-hints":
        result["capabilities"]["li_corpus_truth"]["hints"] = 49
    elif mutation == "admit-provisional-valuation":
        next(x for x in result["terminology"] if x["source_term"] == "valuation")["status"] = "admitted"
    elif mutation == "drop-provisional-valuation":
        result["terminology"] = [x for x in result["terminology"] if x["source_term"] != "valuation"]
    elif mutation == "claim-source-solutions":
        result["capabilities"]["source_support"]["solutions"] = 1
    elif mutation == "expose-learner-answer":
        result["capabilities"]["learner"]["answers_staged_in_closed_details"] = False
    elif mutation == "claim-native-html":
        result["capabilities"]["accessibility"]["native_semantic_html"] = True
    elif mutation == "claim-native-mathml":
        result["capabilities"]["accessibility"]["native_mathml"] = True
    elif mutation == "claim-tagged-pdf":
        result["capabilities"]["accessibility"]["tagged_pdf_claimed"] = True
    elif mutation == "claim-wcag":
        result["capabilities"]["accessibility"]["wcag_conformance_claimed"] = True
    elif mutation == "claim-assistive-testing":
        result["capabilities"]["accessibility"]["assistive_technology_testing_claimed"] = True
    elif mutation == "claim-full-native-roundtrip":
        result["capabilities"]["reproducibility"]["full_native_roundtrip"] = True
    elif mutation == "claim-pdf-byte-replay":
        result["capabilities"]["reproducibility"]["pdf_byte_replay"] = True
    elif mutation == "stale-publication-state":
        result["evidence"]["record_id"] = 0
    elif mutation == "drop-route-stage":
        result["stages"] = result["stages"][:-1]
    elif mutation == "drop-route-node":
        result["units"] = result["units"][:-1]
        result["routes"] = result["routes"][:-1]
    elif mutation == "alter-route-edge":
        result["relations"][0]["from"] = "O013-P06"
    elif mutation == "drop-diagnostic":
        diagnostic_id = result["diagnostics"][-1]["id"]
        result["diagnostics"] = result["diagnostics"][:-1]
        for unit in result["learning_map"]["units"]:
            unit["exercises"] = [exercise for exercise in unit["exercises"] if exercise["id"] != diagnostic_id]
    elif mutation == "drop-mastery":
        result["mastery"] = result["mastery"][:-1]
    elif mutation == "drop-mastery-hint":
        result["mastery"][0]["hints"] = result["mastery"][0]["hints"][:-1]
    elif mutation == "drop-mastery-answer":
        result["mastery"][0]["answer"] = {}
    elif mutation == "fabricate-root-map":
        result["units"][6]["native_root_ids"] = ["root.fabricated"]
    elif mutation == "drop-rights-record":
        result["rights"] = [x for x in result["rights"] if x["rights_id"] != "d70:rights:original-route"]
    elif mutation == "copy-native-body":
        result["native_roots"][0]["body"] = "copied"
    elif mutation == "flatten-source-locale":
        result["components"][0]["source_locale"] = "en"
    elif mutation == "alter-public-artifact-hash":
        result["evidence"]["public_files"][0]["sha256"] = "0" * 64
    elif mutation == "drop-li-adjustment":
        result["corrections"] = result["corrections"][1:]
    elif mutation == "treat-cring-bridge-as-source":
        result["original_bridges"][0]["authorship"] = "source_author"
    else:
        raise D70Error(f"unknown negative mutation: {mutation}")
    return result


def safe_relative_path(value: str) -> PurePosixPath:
    if not value or "\\" in value:
        raise D70Error(f"noncanonical relative path: {value!r}")
    parsed = PurePosixPath(value)
    if parsed.is_absolute() or any(part in {"", ".", ".."} for part in parsed.parts):
        raise D70Error(f"unsafe relative path: {value!r}")
    if parsed.as_posix() != value:
        raise D70Error(f"noncanonical relative path: {value!r}")
    return parsed


def tree_identity(root: Path, relative_paths: Iterable[str]) -> dict[str, Any]:
    normalized = [safe_relative_path(x).as_posix() for x in relative_paths]
    if len(normalized) != len(set(normalized)):
        raise D70Error("duplicate paths in tree identity")
    rows = []
    resolved_root = root.resolve()
    for relative in sorted(normalized):
        path = (root / PurePosixPath(relative)).resolve()
        if path != resolved_root and resolved_root not in path.parents:
            raise D70Error(f"path escapes tree: {relative}")
        identity = file_identity(path)
        rows.append(f"{relative}|{identity['bytes']}|{identity['sha256']}\n")
    data = "".join(rows).encode("utf-8")
    return {"files": len(rows), "sha256": sha256_bytes(data)}
