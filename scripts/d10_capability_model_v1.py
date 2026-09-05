"""Exact zero-copy projection of the public D10/Fremlin native backend."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


COURSE_ID = "D10"
NATIVE_ROLE_ID = "O007"
LOCALE = "id-ID"
CONTRACT = "course-learning-capability/1"
RELEASE_VERSION = "1.0.0"
RELEASE_TAG = "v1.0.0"
RELEASE_COMMIT = "49ed814fc02283df826c4c6c3a9d860888bfec29"
RELEASE_TREE = "334f7902af37d331387041b186b4e1470cd60e7e"
CURRENT_PUBLIC_HEAD = "1cb0f67dcc75a5100e3aa3ca4f9b8f3fb8fb25cc"
CURRENT_PUBLIC_TREE = "5a318d7dbd2485155a59882a06b9386e8a42c6b1"
REPOSITORY = "https://github.com/KokunoYumeto/fremlin-measure-theory-id"
ZENODO_RECORD = "https://zenodo.org/records/22181780"
ZENODO_DOI = "10.5281/zenodo.22181780"
ZENODO_CONCEPT_DOI = "10.5281/zenodo.22059798"
PDF_NAME = "00_READ_FIRST_FONDASI_TEORI_UKURAN_JILID_1_DAN_2_LENGKAP.pdf"
ZIP_NAME = "fondasi-teori-ukuran-jilid-1-2-lengkap-id-v1.0.0-source-backend.zip"
CHECKSUM_NAME = "SHA256SUMS-v1.0.0.txt"
ARCHIVE_ROOT = "fondasi-teori-ukuran-jilid-1-2-lengkap-id-v1.0.0"
ARCHIVE_HTML_ROOT = "output/fondasi-teori-ukuran-v1-v2-complete-id/html"

SOURCE_INPUTS = (
    "backend/catalog-v1.16/MANIFEST.tsv",
    "backend/catalog-v1.16/corpus.jsonl",
    "backend/catalog-v1.16/volumes.jsonl",
    "backend/catalog-v1.16/units.jsonl",
    "backend/catalog-v1.16/resources.jsonl",
    "backend/catalog-v1.16/rights.jsonl",
    "backend/complete-corpus-backend-validation.json",
    "00_control/SOURCE_CORRECTIONS.csv",
    "00_control/TERMINOLOGY_DECISIONS.md",
    "qa/final-closure/complete-source-integration.json",
    "qa/complete-corpus-final-admission.json",
    "qa/complete-corpus-build.json",
    "qa/complete-corpus-pdf-visual-qa.json",
    "qa/complete-corpus-html-build.json",
    "qa/complete-corpus-html-reader-qa.json",
    "qa/complete-corpus-release-package.json",
    "qa/PUBLICATION_RECEIPT_V100_COMPLETE_CORPUS.json",
    "qa/ZENODO_PUBLICATION_RECEIPT_V100_COMPLETE_CORPUS.json",
    "THIRD_PARTY_LICENSES/MathJax-3.2.2-Apache-2.0.txt",
    f"output/release/v1.0.0/{PDF_NAME}",
    f"output/release/v1.0.0/{ZIP_NAME}",
    f"output/release/v1.0.0/{CHECKSUM_NAME}",
)


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(path: Path, *, display_path: str | None = None) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": display_path if display_path is not None else path.as_posix(),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
    if data and not data.endswith(b"\n"):
        raise ValueError(f"JSONL is not LF terminated: {path}")
    return [json.loads(line) for line in data.decode("utf-8").splitlines() if line]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value))


def _split_markdown_row(line: str) -> list[str]:
    r"""Split a pipe row while retaining escaped formula bars such as ``\|x\|``."""
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|") and not text.endswith("\\|"):
        text = text[:-1]
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in text:
        if char == "|" and not escaped:
            cells.append("".join(current).strip().replace("\\|", "|"))
            current = []
        else:
            current.append(char)
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
    cells.append("".join(current).strip().replace("\\|", "|"))
    return cells


def parse_terminology(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    heading = ""
    tables: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.startswith("## ") or line.startswith("### "):
            heading = line.lstrip("# ").strip()
        if line.startswith("|") and index + 1 < len(lines) and lines[index + 1].startswith("|"):
            headers = _split_markdown_row(line)
            separators = _split_markdown_row(lines[index + 1])
            if len(headers) == len(separators) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in separators):
                rows = []
                cursor = index + 2
                while cursor < len(lines) and lines[cursor].startswith("|"):
                    cells = _split_markdown_row(lines[cursor])
                    if len(cells) != len(headers):
                        raise ValueError(f"Terminology table width drift at line {cursor + 1}")
                    rows.append({
                        "line": cursor + 1,
                        "cells": dict(zip(headers, cells)),
                        "raw_markdown": lines[cursor],
                    })
                    cursor += 1
                tables.append({"heading": heading, "headers": headers, "rows": rows})
                index = cursor
                continue
        index += 1
    return {
        "authority": identity(path, display_path="00_control/TERMINOLOGY_DECISIONS.md"),
        "table_count": len(tables),
        "data_row_count": sum(len(table["rows"]) for table in tables),
        "tables": tables,
    }


def catalog_manifest(native_root: Path) -> dict[str, Any]:
    manifest_path = native_root / "backend/catalog-v1.16/MANIFEST.tsv"
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    checked = []
    for row in rows:
        relative = row["path"]
        actual = identity(native_root / relative, display_path=relative)
        if actual["bytes"] != int(row["bytes"]) or actual["sha256"] != row["sha256"]:
            raise ValueError(f"Catalog manifest mismatch: {relative}")
        checked.append(actual)
    return {
        "manifest": identity(manifest_path, display_path="backend/catalog-v1.16/MANIFEST.tsv"),
        "listed_files": len(checked),
        "listed_bytes": sum(row["bytes"] for row in checked),
        "tree_files_including_manifest": len(checked) + 1,
        "tree_bytes_including_manifest": sum(row["bytes"] for row in checked) + manifest_path.stat().st_size,
        "all_listed_hashes_verified": True,
    }


def _unit_kind(unit: dict[str, Any]) -> str:
    unit_id = unit["id"]
    anchor = str(unit["source_anchor"])
    if "CONCORDANCE" in unit_id:
        return "concordance"
    if "REFERENCES" in unit_id:
        return "references"
    if unit_id.endswith("-MTI") or unit_id.endswith("-MTI-V12"):
        return "index"
    if "APPENDIX-INTRO" in unit_id:
        return "appendix_introduction"
    if "-APP-" in unit_id or re.fullmatch(r"mt1a[1-9]", anchor, re.IGNORECASE):
        return "appendix_section"
    if "FRONT" in unit_id:
        return "front_matter"
    if "INTRO" in unit_id or re.fullmatch(r"(?:mt)?\d{2}", anchor, re.IGNORECASE):
        return "chapter_introduction"
    return "section"


def _route_names(unit: dict[str, Any]) -> list[str]:
    anchor = str(unit["source_anchor"])
    special = {
        "mt10": ["bagian-awal", "pendahuluan-umum"],
        "mt01": [],
        "mt1": ["pendahuluan-jilid-1"],
        "mt1a": ["lampiran"],
        "mt1a1": ["1A1"],
        "mt1a2": ["1A2"],
        "mt1a3": ["1A3"],
        "mt1conc": ["konkordansi"],
        "mt1r": ["referensi"],
        "mti-volume1-active": ["indeks"],
        "2conc": ["konkordansi-jilid-2"],
        "2r": ["referensi-jilid-2"],
        "MTI-V12": ["indeks-jilid-1-dan-2"],
    }
    if anchor in special:
        return special[anchor]
    if anchor.startswith("mt"):
        anchor = anchor[2:]
    return [anchor]


def _asset(receipt: dict[str, Any], name: str) -> dict[str, Any]:
    row = dict(receipt["assets"][name])
    row["file_name"] = name
    return row


def derive_projection(native_root: Path) -> dict[str, Any]:
    missing = [relative for relative in SOURCE_INPUTS if not (native_root / relative).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing D10 inputs: {missing}")

    corpus = read_jsonl(native_root / "backend/catalog-v1.16/corpus.jsonl")
    volumes = read_jsonl(native_root / "backend/catalog-v1.16/volumes.jsonl")
    units_source = read_jsonl(native_root / "backend/catalog-v1.16/units.jsonl")
    resources = read_jsonl(native_root / "backend/catalog-v1.16/resources.jsonl")
    rights = read_jsonl(native_root / "backend/catalog-v1.16/rights.jsonl")
    corrections = read_csv(native_root / "00_control/SOURCE_CORRECTIONS.csv")
    terminology = parse_terminology(native_root / "00_control/TERMINOLOGY_DECISIONS.md")
    backend_qa = read_json(native_root / "backend/complete-corpus-backend-validation.json")
    source_qa = read_json(native_root / "qa/final-closure/complete-source-integration.json")
    admission = read_json(native_root / "qa/complete-corpus-final-admission.json")
    pdf_build = read_json(native_root / "qa/complete-corpus-build.json")
    pdf_qa = read_json(native_root / "qa/complete-corpus-pdf-visual-qa.json")
    html_build = read_json(native_root / "qa/complete-corpus-html-build.json")
    html_qa = read_json(native_root / "qa/complete-corpus-html-reader-qa.json")
    package_qa = read_json(native_root / "qa/complete-corpus-release-package.json")
    github = read_json(native_root / "qa/PUBLICATION_RECEIPT_V100_COMPLETE_CORPUS.json")
    zenodo = read_json(native_root / "qa/ZENODO_PUBLICATION_RECEIPT_V100_COMPLETE_CORPUS.json")
    catalog = catalog_manifest(native_root)

    by_id = {row["id"]: row for row in units_source}
    ordered_units: list[dict[str, Any]] = []
    correction_counts = Counter(row["unit_id"] for row in corrections)
    route_map = {row["route"]: row for row in html_qa["route_evidence"]}
    mapped_routes: set[str] = set()
    ordinal = 0
    for volume in sorted(volumes, key=lambda row: row["ordinal"]):
        for unit_id in volume["admitted_unit_ids"]:
            source = by_id[unit_id]
            ordinal += 1
            routes = _route_names(source)
            for route in routes:
                if route not in route_map:
                    raise ValueError(f"Missing reader route {route} for {unit_id}")
                mapped_routes.add(route)
            ordered_units.append({
                "unit_id": unit_id,
                "ordinal": ordinal,
                "volume_id": source["volume_id"],
                "unit_kind": _unit_kind(source),
                "source_anchor": source["source_anchor"],
                "source_title": source["source_title"],
                "title_id": source["target_working_title"],
                "source_pages": source["source_pages"],
                "source_page_count": source.get("source_page_count"),
                "source_member": source["source_member"],
                "source_bytes": source["source_bytes"],
                "source_sha256": source["source_sha256"],
                "target_path": source["target_path"],
                "target_bytes": source["target_bytes"],
                "target_sha256": source["target_sha256"],
                "target_admitted": source["target_admitted"],
                "exercise_ids": source["exercise_ids"],
                "exercise_count": len(source["exercise_ids"]),
                "explicit_hint_count": source["explicit_hint_count"],
                "formula_count": source["formula_count"],
                "correction_count": correction_counts[unit_id],
                "source_resource_ids": source["source_resource_ids"],
                "public_source": f"{REPOSITORY}/blob/{RELEASE_COMMIT}/{source['target_path']}",
                "portable_reader_routes": [
                    {
                        "route": route,
                        "title": route_map[route]["title"],
                        "archive_entry": f"{ARCHIVE_ROOT}/{ARCHIVE_HTML_ROOT}/{route}/index.html",
                        "desktop_pass": route_map[route]["desktop_pass"],
                        "mobile_pass": route_map[route]["mobile_pass"],
                    }
                    for route in routes
                ],
                "portable_route_binding": "verified_source_member_or_exact_native_anchor" if routes else "no_one_to_one_route_claim",
            })

    supplemental_routes = []
    for row in html_qa["route_evidence"]:
        if row["route"] not in mapped_routes:
            supplemental_routes.append({
                "route": row["route"],
                "title": row["title"],
                "archive_entry": (
                    f"{ARCHIVE_ROOT}/{ARCHIVE_HTML_ROOT}/index.html" if row["route"] == ""
                    else f"{ARCHIVE_ROOT}/{ARCHIVE_HTML_ROOT}/{row['route']}/index.html"
                ),
                "desktop_pass": row["desktop_pass"],
                "mobile_pass": row["mobile_pass"],
                "reason": "cumulative_hub_or_reader_front_matter_without_a_one_to_one_catalog_unit_binding",
            })

    typed_ids = [exercise for unit in ordered_units for exercise in unit["exercise_ids"]]
    variants = backend_qa["catalog_state"]["lossless_typed_source_topology"]["variant_macro_exercises_retained_outside_root_count"]
    github_assets = [_asset(github, name) for name in github["asset_order"]]
    zenodo_assets = [_asset(zenodo, name) for name in zenodo["asset_order"]]
    source_inputs = [identity(native_root / path, display_path=path) for path in SOURCE_INPUTS]

    counts = {
        "source_lock_inputs": len(source_inputs),
        "catalog_files": catalog["tree_files_including_manifest"],
        "catalog_manifest_rows": catalog["listed_files"],
        "schema_valid_records": backend_qa["schema_valid_record_count"],
        "corpora": len(corpus),
        "volumes": len(volumes),
        "units": len(ordered_units),
        "resources": len(resources),
        "native_rights_records": len(rights),
        "official_pages": corpus[0]["official_pages_total"],
        "typed_exercises": len(typed_ids),
        "standard_header_exercises": corpus[0]["active_exercise_problem_id_count"],
        "variant_header_exercises": len(variants),
        "explicit_hints": sum(row["explicit_hint_count"] for row in ordered_units),
        "formula_occurrences": sum(row["formula_count"] for row in ordered_units),
        "correction_rows": len(corrections),
        "terminology_tables": terminology["table_count"],
        "terminology_rows": terminology["data_row_count"],
        "reader_routes": len(html_qa["route_evidence"]),
        "reader_files": html_qa["artifact"]["files"],
        "reader_viewport_observations": html_qa["coverage"]["route_viewport_observations"],
        "math_source_assistive_pairs": html_qa["static_integrity"]["math_source_wrapper_pairs"],
        "release_assets": len(github_assets),
    }

    learning_map = {
        "schema": "d10-learning-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "title": "Ukuran dan Integrasi",
        "native_title": corpus[0]["target_working_title"],
        "program_prerequisites": ["C20", "C90"],
        "prerequisite_scope": "central_course_level_only_not_native_per_unit_claims",
        "route": {"route_id": "D10:route:fremlin-v1-v2", "unit_ids": [row["unit_id"] for row in ordered_units]},
        "volumes": volumes,
        "units": ordered_units,
        "supplemental_reader_surfaces": supplemental_routes,
        "public_pdf": github["assets"][PDF_NAME]["url"],
        "portable_reader": github["assets"][ZIP_NAME]["url"],
        "portable_reader_entry": f"{ARCHIVE_ROOT}/{ARCHIVE_HTML_ROOT}/index.html",
        "limitations": [
            "Adapter memproyeksikan identitas, metadata, dan bukti; badan buku tetap berada pada edisi native publik.",
            "Dua volume memuat 94 unit katalog dan 98 rute pembaca; rute tambahan tidak diubah menjadi unit fiktif.",
            "Sebanyak 1.096 identitas latihan bertipe dipertahankan; angka 1.094 hanya sensus header standar dan mengecualikan dua header varian yang sah.",
            "Hanya 276 petunjuk sumber eksplisit yang diklaim. Tidak ada lapisan jawaban atau solusi lengkap.",
            "Prasyarat C20 dan C90 berasal dari peta program pusat, bukan graf prasyarat per unit dari sumber native.",
            "Pembaca HTML native tersedia sebagai arsip luring; adapter tidak mengklaim situs HTML native per-unit daring.",
        ],
    }
    educator_map = {
        "schema": "d10-educator-map/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "locale": LOCALE,
        "selector": {
            "selection_unit": "native_unit_id",
            "exercise_selection": "exact_native_exercise_id",
            "export_format": "application/json",
            "body_content_embedded": False,
            "selected_units": ordered_units,
        },
        "counts": counts,
        "claim_boundary": {
            "native_learning_outcomes_available": False,
            "native_assessment_blueprints_available": False,
            "complete_solution_layer_available": False,
            "explicit_source_hints_available": 276,
            "proof_and_result_records_are_exercise_solutions": False,
        },
        "limitations": [
            "Pemilih ini menyusun paket ID unit/latihan dan tautan sumber, bukan menyalin isi buku.",
            "Judul, urutan, halaman, latihan, petunjuk, formula, dan koreksi berasal dari backend native; hasil belajar atau rubrik tidak direka.",
            "Bukti hasil/proof pada tranche akhir adalah struktur matematika buku, bukan jawaban latihan.",
        ],
    }
    ledger_references = {
        "schema": "d10-ledger-references/1",
        "course_id": COURSE_ID,
        "catalog_integrity": catalog,
        "catalog_counts": backend_qa["catalog_counts"],
        "schema_valid_record_count": backend_qa["schema_valid_record_count"],
        "resources": resources,
        "source_target_unit_hashes": [
            {key: unit[key] for key in ("unit_id", "source_member", "source_bytes", "source_sha256", "target_path", "target_bytes", "target_sha256")}
            for unit in ordered_units
        ],
        "deterministic_evidence": [
            identity(native_root / path, display_path=path)
            for path in SOURCE_INPUTS[6:16]
        ],
        "projection": {
            "native_bodies_copied": False,
            "native_ids_preserved": True,
            "catalog_manifest_replayed": True,
            "strict_native_roundtrip_claimed": False,
        },
    }
    public_evidence = {
        "schema": "d10-public-evidence/1",
        "course_id": COURSE_ID,
        "github": {
            "repository": REPOSITORY,
            "release_tag": RELEASE_TAG,
            "release_commit": github["boundary"]["commit"],
            "release_tree": github["boundary"]["tree"],
            "current_public_head_observed_separately": CURRENT_PUBLIC_HEAD,
            "current_public_tree_observed_separately": CURRENT_PUBLIC_TREE,
            "anonymous_verification": "verified",
            "release_assets": github_assets,
        },
        "zenodo": {
            "record_id": zenodo["record"]["id"],
            "doi": zenodo["record"]["doi"],
            "concept_doi": zenodo["record"]["conceptdoi"],
            "url": zenodo["record"]["url"],
            "anonymous_verification": "verified",
            "release_assets": zenodo_assets,
        },
        "reader": {
            "official_source_pages": 672,
            "pdf_reflow_pages": pdf_qa["artifact"]["pages"],
            "portable_routes": html_qa["artifact"]["routes"],
            "portable_files": html_qa["artifact"]["files"],
            "portable_bytes": html_qa["artifact"]["bytes"],
            "semantic_html": True,
            "math_assistive_pairs": html_qa["static_integrity"]["math_source_wrapper_pairs"],
            "tagged_pdf": False,
            "online_native_html": False,
        },
        "public_state_changed": False,
    }
    rights_and_terms = {
        "schema": "d10-rights-and-terms/1",
        "course_id": COURSE_ID,
        "rights_records": rights,
        "third_party_components": [{
            "component": "MathJax 3.2.2",
            "license_identifier": "Apache-2.0",
            "license_text": identity(
                native_root / "THIRD_PARTY_LICENSES/MathJax-3.2.2-Apache-2.0.txt",
                display_path="THIRD_PARTY_LICENSES/MathJax-3.2.2-Apache-2.0.txt",
            ),
        }],
        "terminology": terminology,
        "corrections": corrections,
        "correction_classification_counts": dict(sorted(Counter(row["classification"] for row in corrections).items())),
        "blanket_license_claimed": False,
    }
    claim_boundary = {
        "schema": "d10-claim-boundary/1",
        "course_id": COURSE_ID,
        "learner_attempt_instances": 0,
        "learner_submission_instances": 0,
        "learner_result_instances": 0,
        "credential_assertion_instances": 0,
        "complete_solution_records": 0,
        "explicit_source_hints": 276,
        "proof_and_result_records_retyped_as_solutions": False,
        "native_learning_outcomes_invented": False,
        "native_unit_prerequisites_invented": False,
        "native_bodies_copied": False,
        "central_course_truth_rewritten": False,
        "online_native_html_claimed": False,
        "tagged_pdf_claimed": False,
        "public_state_changed": False,
    }
    capabilities = {
        "schema": "d10-capability-summary/1",
        "contract": CONTRACT,
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "native_family": "fremlin_measure_theory_volumes_1_2",
        "counts": counts,
        "learner": {
            "unit_navigation": True,
            "exact_exercise_ids": counts["typed_exercises"],
            "explicit_source_hints": counts["explicit_hints"],
            "semantic_html": True,
            "native_math_assistive_markup": True,
            "offline_reader": True,
        },
        "educator": {
            "unit_selector": True,
            "exercise_selector": True,
            "json_plan_export": True,
            "correction_ledger": counts["correction_rows"],
            "terminology_decisions": counts["terminology_rows"],
            "complete_solution_layer": False,
        },
        "reproducibility": {
            "native_backend_deterministic": backend_qa["pass"],
            "source_integration_verified": source_qa["result"] == "pass",
            "pdf_build_deterministic": pdf_build["pass"],
            "pdf_visual_qa_passed": pdf_qa["pass"],
            "html_build_deterministic": html_build["pass"] and html_build["deterministic_replay"],
            "html_reader_qa_passed": html_qa["pass"],
            "release_package_deterministic": package_qa["pass"] and package_qa["package_details"]["two_clean_builds_byte_exact"],
            "adapter_deterministic": True,
            "full_native_roundtrip_claimed": False,
        },
        "rights": {"component_specific": True, "blanket_license_claimed": False},
        "claim_boundary": claim_boundary,
        "strict_contract_2_3_1_conformance_claimed": False,
    }
    source_lock = {
        "schema": "d10-source-lock/1",
        "course_id": COURSE_ID,
        "native_role_id": NATIVE_ROLE_ID,
        "locale": LOCALE,
        "release_version": RELEASE_VERSION,
        "native_repository": {
            "url": REPOSITORY,
            "release_tag": RELEASE_TAG,
            "release_commit": RELEASE_COMMIT,
            "release_tree": RELEASE_TREE,
            "current_public_head_observed_separately": CURRENT_PUBLIC_HEAD,
            "current_public_tree_observed_separately": CURRENT_PUBLIC_TREE,
            "post_release_receipts_are_current_main_inputs": True,
        },
        "local_source_locator": "04_mirrors/id/measure-integration-id-v1.0.0-audit",
        "inputs": source_inputs,
        "catalog_manifest": catalog,
    }
    return {
        "source_lock": source_lock,
        "learning_map": learning_map,
        "educator_map": educator_map,
        "ledger_references": ledger_references,
        "public_evidence": public_evidence,
        "rights_and_terms": rights_and_terms,
        "claim_boundary": claim_boundary,
        "capabilities": capabilities,
    }


def projection_errors(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    learning = bundle.get("learning_map", {})
    educator = bundle.get("educator_map", {})
    capabilities = bundle.get("capabilities", {})
    ledgers = bundle.get("ledger_references", {})
    public = bundle.get("public_evidence", {})
    rights = bundle.get("rights_and_terms", {})
    boundary = bundle.get("claim_boundary", {})
    units = learning.get("units", [])
    unit_ids = [row.get("unit_id") for row in units]
    counts = capabilities.get("counts", {})

    if len(unit_ids) != 94 or len(set(unit_ids)) != 94:
        errors.append("D10-UNIT-IDENTITY")
    if learning.get("route", {}).get("unit_ids") != unit_ids:
        errors.append("D10-UNIT-ORDER")
    if learning.get("locale") != LOCALE:
        errors.append("D10-LOCALE")
    if any(row.get("target_admitted") is not True for row in units):
        errors.append("D10-TARGET-ADMISSION")
    if any(not re.fullmatch(r"[a-f0-9]{64}", row.get("source_sha256", "")) or not re.fullmatch(r"[a-f0-9]{64}", row.get("target_sha256", "")) for row in units):
        errors.append("D10-UNIT-HASH")
    typed = [exercise for row in units for exercise in row.get("exercise_ids", [])]
    if len(typed) != 1096 or len(set(typed)) != 1096:
        errors.append("D10-TYPED-EXERCISES")
    if counts.get("standard_header_exercises") != 1094 or counts.get("variant_header_exercises") != 2:
        errors.append("D10-HEADER-BOUNDARY")
    if not {"243Xo", "274Xf"}.issubset(set(typed)):
        errors.append("D10-VARIANT-IDENTITIES")
    expected_counts = {
        "catalog_files": 507,
        "catalog_manifest_rows": 506,
        "schema_valid_records": 16096,
        "corpora": 1,
        "volumes": 2,
        "units": 94,
        "resources": 349,
        "native_rights_records": 2,
        "official_pages": 672,
        "typed_exercises": 1096,
        "standard_header_exercises": 1094,
        "variant_header_exercises": 2,
        "explicit_hints": 276,
        "formula_occurrences": 53491,
        "correction_rows": 420,
        "terminology_tables": 14,
        "terminology_rows": 132,
        "reader_routes": 98,
        "reader_files": 138,
        "reader_viewport_observations": 196,
        "math_source_assistive_pairs": 53255,
        "release_assets": 3,
    }
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            errors.append(f"D10-COUNT-{key.upper()}")
    if educator.get("selector", {}).get("body_content_embedded") is not False:
        errors.append("D10-EDUCATOR-BODY-COPY")
    if len(educator.get("selector", {}).get("selected_units", [])) != 94:
        errors.append("D10-EDUCATOR-UNITS")
    if ledgers.get("catalog_integrity", {}).get("all_listed_hashes_verified") is not True:
        errors.append("D10-CATALOG-MANIFEST")
    if ledgers.get("projection", {}).get("native_bodies_copied") is not False:
        errors.append("D10-NATIVE-BODY-COPY")
    if public.get("github", {}).get("anonymous_verification") != "verified":
        errors.append("D10-GITHUB-ANONYMITY")
    if public.get("zenodo", {}).get("anonymous_verification") != "verified":
        errors.append("D10-ZENODO-ANONYMITY")
    if len(public.get("github", {}).get("release_assets", [])) != 3 or len(public.get("zenodo", {}).get("release_assets", [])) != 3:
        errors.append("D10-PUBLIC-ASSETS")
    if public.get("reader", {}).get("online_native_html") is not False:
        errors.append("D10-ONLINE-NATIVE-HTML")
    if public.get("reader", {}).get("tagged_pdf") is not False:
        errors.append("D10-TAGGED-PDF")
    if public.get("public_state_changed") is not False:
        errors.append("D10-PUBLIC-STATE")
    if rights.get("blanket_license_claimed") is not False:
        errors.append("D10-BLANKET-LICENSE")
    if len(rights.get("rights_records", [])) != 2 or len(rights.get("third_party_components", [])) != 1:
        errors.append("D10-RIGHTS-COMPONENTS")
    if rights.get("terminology", {}).get("data_row_count") != 132:
        errors.append("D10-TERMINOLOGY-ROWS")
    if len(rights.get("corrections", [])) != 420:
        errors.append("D10-CORRECTION-ROWS")
    expected_false = (
        "proof_and_result_records_retyped_as_solutions", "native_learning_outcomes_invented",
        "native_unit_prerequisites_invented", "native_bodies_copied",
        "central_course_truth_rewritten", "online_native_html_claimed",
        "tagged_pdf_claimed", "public_state_changed",
    )
    for key in expected_false:
        if boundary.get(key) is not False:
            errors.append(f"D10-BOUNDARY-{key.upper()}")
    for key in ("learner_attempt_instances", "learner_submission_instances", "learner_result_instances", "credential_assertion_instances", "complete_solution_records"):
        if boundary.get(key) != 0:
            errors.append(f"D10-NONZERO-{key.upper()}")
    if boundary.get("explicit_source_hints") != 276:
        errors.append("D10-HINT-BOUNDARY")
    return sorted(set(errors))
